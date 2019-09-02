import argparse
import os
import subprocess
from typing import Iterator
from helper import makesurePandoc

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


def process(inputdir, outputdir):
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
      
      subprocess.call([pandoc, '--filter', 'customfilter.py', '--reference-doc', 'customref.docx', inputfile, '-o', outputfile, '--resource-path', os.path.dirname(inputfile)])
      subprocess.call(['python', 'fixEqNum.py', outputfile])

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('inputdir',
                      help='input folder')
  parser.add_argument('outputdir', nargs='?', default='',
                      help='output folder')
  args = parser.parse_args()

  process(args.inputdir, args.outputdir)

      