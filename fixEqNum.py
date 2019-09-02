import argparse
import os
import zipfile
from lxml import etree
import sys

def processMathInXml(buffer):
  root = etree.fromstring(buffer)
  for mathPara in root.findall('.//{%s}oMathPara'%root.nsmap['m']):
    for math in mathPara.findall('{%s}oMath'%root.nsmap['m']):
      if math.find('{%s}eqArr'%root.nsmap['m']):
        continue
      eqArr = etree.Element('{%s}eqArr'%root.nsmap['m'])
      eqArrPr = etree.SubElement(eqArr, '{%s}eqArrPr'%root.nsmap['m'])
      maxDist = etree.SubElement(eqArrPr, '{%s}maxDist'%root.nsmap['m'])
      maxDist.attrib['{%s}val'%root.nsmap['m']] = '1'
      e = etree.SubElement(eqArr, '{%s}e'%root.nsmap['m'])
      for item in math:
        math.remove(item)
        e.append(item)
      math.append(eqArr)
  return etree.tostring(root)


def fixEqNum(docx, new):
  zin = zipfile.ZipFile (docx, 'r')
  subNames = os.path.splitext(docx)
  outfile = subNames[0] + '_fixed' + subNames[1]
  zout = zipfile.ZipFile (outfile, 'w')
  for item in zin.infolist():
    buffer = zin.read(item.filename)
    if item.filename == 'word/document.xml':
      buffer = processMathInXml(buffer)
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

  fixEqNum(args.docx, args.new)
