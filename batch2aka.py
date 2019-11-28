import argparse
import os
import sys
import subprocess
from typing import Iterator
from helper import makesurePandoc
import json
import re
import csv
from requests.utils import requote_uri

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

  with open('aka.csv', 'w', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file, dialect='excel')
    writer.writerow(['ShortUrl', 'TargetUrl', 'MobileUrl', 'Owners', 'GroupOwner'])

    inputfiles = find_all_files_with_extension(inputdir, ".md")
    for inputfile in inputfiles:
      if 'Step' not in inputfile:
        continue
      inputfilename = os.path.split(inputfile)[1]
      if not re.match(r'\d+.\d+-*', inputfilename):
        continue
      
      ret = re.search(r'(\d+).(\d+)-*', inputfilename)
      shorturl=f'9StepsCh{ret[1]}Sec{ret[2]}'
      targeturl=re.sub(r'^.*B-教学案例与实践', 'https://github.com/microsoft/ai-edu/tree/master/B-教学案例与实践', inputfile)
      targeturl=re.sub(r'\\', '/', targeturl)
      targeturl=requote_uri(targeturl)
      # targeturl=f''
      print(shorturl)
      print(targeturl)
      print(inputfile)
      writer.writerow([
        shorturl,
        targeturl,
        '',
        'lchao',
        'aieduaka'        
      ])

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

    
