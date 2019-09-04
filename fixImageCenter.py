import argparse
import os
import zipfile
from lxml import etree
import sys

def processImageCenterInXml(buffer):
  root = etree.fromstring(buffer)
  for picEle in root.findall('.//{%s}pic'%root.nsmap['pic']):
    pEle = picEle.getparent()
    while pEle != root:
      if pEle.tag != '{%s}p'%root.nsmap['w']:
        pEle = pEle.getparent()
        continue
      pPrEle = pEle.find('{%s}pPr'%root.nsmap['w'])
      if pPrEle is None:
        pPrEle = etree.SubElement(pEle, '{%s}pPr'%root.nsmap['w'])
      jcEle = pPrEle.find('{%s}jc'%root.nsmap['w'])
      if jcEle is None:
        jcEle = etree.SubElement(pPrEle, '{%s}jc'%root.nsmap['w'])
      jcEle.attrib['{%s}val'%root.nsmap['w']] = 'center'
      break
  return etree.tostring(root)


def fixImageCenter(docx, new):
  zin = zipfile.ZipFile (docx, 'r')
  subNames = os.path.splitext(docx)
  outfile = subNames[0] + '_fixed_center' + subNames[1]
  zout = zipfile.ZipFile (outfile, 'w')
  for item in zin.infolist():
    buffer = zin.read(item.filename)
    if item.filename == 'word/document.xml':
      buffer = processImageCenterInXml(buffer)
      zout.writestr(item, buffer)
    else:
      zout.writestr(item, buffer)
  zout.close()
  zin.close()

  if not new:
    try:
      os.replace(outfile, docx)
    except Exception as ex:
      print('rename %s to %s failed'%(outfile, docx))


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('docx',
                      help='source docx file')
  parser.add_argument('--new', action='store_true',
                      help='save result in new file')
  args = parser.parse_args()

  if os.path.splitext(args.docx)[1] != '.docx' or not os.path.exists(args.docx):
    print('Invalid docx args')
    sys.exit(1)

  fixImageCenter(args.docx, args.new)
