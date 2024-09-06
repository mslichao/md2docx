import os
import tarfile
import zipfile
from pathlib import Path

import requests


def makesurePandoc():
  if '__file__' in globals():
    tools_path = Path(__file__).parent / 'bin'
  else:
    tools_path = Path.cwd() / 'bin'

  pandoc_version = '3.3'
  pandoc_dir = tools_path / f'pandoc-{pandoc_version}'
  pandoc_bin = pandoc_dir / 'pandoc.exe' if os.name == 'nt' else pandoc_dir / 'pandoc'
    
  if pandoc_bin.exists():
    return pandoc_bin

  if os.name == 'nt':
    url = f'https://github.com/jgm/pandoc/releases/download/{pandoc_version}/pandoc-{pandoc_version}-windows-x86_64.zip'
    local = tools_path / 'pandoc.zip'
  else:
    url = f'https://github.com/jgm/pandoc/releases/download/{pandoc_version}/pandoc-{pandoc_version}-linux-amd64.tar.gz'
    local = tools_path / 'pandoc.tar.gz'

  tools_path.mkdir(parents=True, exist_ok=True)
  with requests.get(url, stream=True) as r:
    r.raise_for_status()
    with open(local, 'wb') as f:
      for chunk in r.iter_content(chunk_size=8192):
          _ = f.write(chunk)

  if os.name == 'nt':
    with zipfile.ZipFile(local, 'r') as zipObj:
      zipObj.extractall(tools_path)
  else:
    with tarfile.open(local) as tar:
      tar.extractall(tools_path)

  if pandoc_bin.exists():
    return pandoc_bin
  else:
    raise FileNotFoundError('Pandoc not found')
