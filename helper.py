import sys
import os
import zipfile
import tarfile

import urllib.request

def makesurePandoc():
  pandoc = os.path.join(os.path.dirname(__file__), 'pandoc.exe' if os.name == 'nt' else 'pandoc')
  if os.path.exists(pandoc):
    return pandoc

  if os.name == 'nt':
    urllib.request.urlretrieve('https://aiedustorage.blob.core.windows.net/tools/pandoc-2.7.3-windows-x86_64.zip', 'pandoc-2.7.3-windows-x86_64.zip')
    with zipfile.ZipFile('pandoc-2.7.3-windows-x86_64.zip', 'r') as zipObj:
      for item in zipObj.infolist():
        if item.filename == 'pandoc-2.7.3-windows-x86_64/pandoc.exe':
          buffer = zipObj.read(item.filename)
          with open(pandoc, 'wb') as f:
            f.write(buffer)
  else:
    urllib.request.urlretrieve('https://aiedustorage.blob.core.windows.net/tools/pandoc-2.7.3-linux.tar.gz', 'pandoc-2.7.3-linux.tar.gz')
    with tarfile.open('pandoc-2.7.3-linux.tar.gz') as tar:
      buffer = tar.extractfile('pandoc-2.7.3/bin/pandoc').read()
      with open(pandoc, 'wb') as f:
        f.write(buffer)
      os.chmod(pandoc, 0o777)

  return pandoc
  
def makesureWkhtmltopdf():
  urllib.request.urlretrieve('https://aiedustorage.blob.core.windows.net/tools/wkhtmltopdf.zip', 'wkhtmltopdf.zip')
  wkhtmltopdf = os.path.join(os.path.dirname(__file__), 'wkhtmltopdf.exe' if os.name == 'nt' else 'wkhtmltopdf')
  if os.path.exists(wkhtmltopdf):
    return wkhtmltopdf

  if os.name == 'nt':
    with zipfile.ZipFile('wkhtmltopdf.zip', 'r') as zipObj:
      for item in zipObj.infolist():
        if item.filename == 'wkhtmltopdf.exe':
          buffer = zipObj.read(item.filename)
          with open(wkhtmltopdf, 'wb') as f:
            f.write(buffer)

  return wkhtmltopdf