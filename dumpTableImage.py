import argparse
import os
import sys
import subprocess
from typing import Iterator
from helper import makesurePandoc
import json


def process(inputfile):
  pandoc = makesurePandoc()
  pandocReadAll = [pandoc, '--filter', 'customfilter.py', inputfile, '-t', 'json']
  jsonString = subprocess.run(pandocReadAll, stdout=subprocess.PIPE).stdout

  originDoc = json.loads(jsonString)
  originBlocks = originDoc['blocks']

  tableBlocks = []
  imageBlocks = []

  for (index, item) in enumerate(originBlocks):
    # print(item)
    if item['t'] == 'Table':
      tableBlocks.append(originBlocks[index - 1])
    if item['t'] == 'Para' and item['c'][0]['t'] == 'Image':
      imageBlocks.append(originBlocks[index + 1])
      
  checkListOrder(tableBlocks, '表')
  checkListOrder(imageBlocks, '图')

  saveList(pandoc, originDoc, tableBlocks, 'table.txt')
  saveList(pandoc, originDoc, imageBlocks, 'image.txt')


def saveList(pandoc, originDoc, blocks, outputfile):
  originDoc['blocks'] = blocks
  jsonString = json.dumps(originDoc)
  pandocWriter = [pandoc, '-f', 'json', '-o', outputfile]  
  subprocess.run(pandocWriter, input=bytes(jsonString, encoding='utf-8'))


def checkListOrder(blocks, preWord):
  clipCount = 100
  chap = 0
  indexInChap = 0
  for item in blocks:
    # print(item)
    try:
      title = str(item['c'][0]['c'])
      if not title.startswith(preWord):
        writeWarning(f'"{preWord}" title not starts with "{preWord}": {title[:clipCount]}')
        continue
      title = title[1:]
      chapAndIndex = title.split('-')
      if int(chapAndIndex[1]) == 1:
        if int(chapAndIndex[0]) <= chap:
          writeWarning(f'"{preWord}" chap number error: {title[:clipCount]}')
        chap = int(chapAndIndex[0])
        indexInChap = int(chapAndIndex[1])
      else:
        if chap != int(chapAndIndex[0]) or indexInChap != (int(chapAndIndex[1]) - 1):
          writeWarning(f'"{preWord}" chap number error: {title[:clipCount]}')
        chap = int(chapAndIndex[0])
        indexInChap = int(chapAndIndex[1])

    except Exception:
      writeWarning(f'"{preWord}" Failed when process {str(item)[:clipCount]}')


def writeWarning(message):
  print(f'Write-Host "##vso[task.logissue]warning {message}"')

  
if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('inputfile',
                      help='markdown file')
  args = parser.parse_args()

  process(args.inputfile)

      