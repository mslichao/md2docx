import argparse
import os
import sys
import subprocess
from typing import Iterator
from helper import makesurePandoc
import json
import re

def find_all_files(directory: str, follow_symlinks=False) -> Iterator[str]:
    for entry in os.scandir(directory):
        name = os.path.join(directory, entry.name)
        if entry.is_dir(follow_symlinks=follow_symlinks):
            yield from find_all_files(name)
        elif entry.is_file(follow_symlinks=follow_symlinks):
            yield os.path.abspath(name)


def find_all_files_with_extension(directory: str,
                                  extension: str,
                                  follow_symlinks=False) \
        -> Iterator[str]:
    return filter(lambda x: x.endswith(extension),
                  find_all_files(directory, follow_symlinks))


def process(inputdir, outputdir, ignore_custom_size):
  inputdir=os.path.abspath(inputdir)
  if outputdir:
    outputdir=os.path.abspath(outputdir)
  else:
    outputdir=inputdir + '_docx'

  if not os.path.exists(inputdir):
    print('Not found input folder')
    return False

  pandoc = makesurePandoc()

  os.makedirs(outputdir, exist_ok=True)

  inputfiles = find_all_files_with_extension(inputdir, ".md")
  for inputfile in inputfiles:
      print(inputfile)
      
      relpath=inputfile.replace(inputdir, '', 1).strip(os.path.sep)
      relpathWithoutExt=os.path.splitext(relpath)[0]
      outputfile=os.path.join(outputdir, relpathWithoutExt+'.docx')
      os.makedirs(os.path.dirname(outputfile), exist_ok=True)
      
      # pandocCmdList = [pandoc, '--dpi', '160', '--filter', 'customfilter.py', '--reference-doc', 'customref.docx', inputfile, '-o', outputfile, '--resource-path', os.path.dirname(inputfile)]
      pandocCmdList = [pandoc, '--filter', 'customfilter.py', inputfile, '-t', 'json']
      if not ignore_custom_size:
        pandocCmdList.append('--filter')
        pandocCmdList.append('customsizefilter.py')

      jsonString = subprocess.run(pandocCmdList, stdout=subprocess.PIPE).stdout
      originDoc = json.loads(jsonString)
      originBlocks = originDoc['blocks']

      tempBlocks = originBlocks[:]
      for (index, item) in enumerate(tempBlocks):
        try:
          if item['t'] == 'Table':
            preItemPara = tempBlocks[index - 1]
            if preItemPara['t'] == 'Para' and re.match(r'表\d+-\d+', preItemPara['c'][0]['c']):
              if len(item['c'][0]) == 0:
                item['c'][0].extend(preItemPara['c'])
                originBlocks.remove(preItemPara)
          elif item['t'] == 'Para' and item['c'][0]['t'] == 'Image':
            nextItemPara = tempBlocks[index + 1]
            if nextItemPara['t'] == 'Para' and re.match(r'图\d+-\d+', nextItemPara['c'][0]['c']):
              image = item['c'][0]['c']
              if not image[2][1]:
                image[2][1] = 'fig:'
                image[1].clear()
                image[1].extend(nextItemPara['c'])
                originBlocks.remove(nextItemPara)
        except Exception:
          pass

      # for item in originBlocks:
      #   print(item)

      jsonString = json.dumps(originDoc)
      pandocWriter = [pandoc, '-f', 'json', '--dpi', '160', '--reference-doc', 'customref.docx', '-o', outputfile, '--resource-path', os.path.dirname(inputfile)]
      subprocess.run(pandocWriter, input=bytes(jsonString, encoding='utf-8'))
      subprocess.call([sys.executable, 'fixEqNum.py', outputfile])
      subprocess.call([sys.executable, 'fixImageCenter.py', outputfile])

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('inputdir',
                      help='input folder')
  parser.add_argument('outputdir', nargs='?', default='',
                      help='output folder')
  parser.add_argument('--ignore_custom_size', action='store_true',
                      help='save result in new file')
  args = parser.parse_args()

  process(args.inputdir, args.outputdir, args.ignore_custom_size)

      