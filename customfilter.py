from pandocfilters import toJSONFilter, toJSONFilters, Math, Para, Image, RawInline, Str
import sys
import re
import os


def processImage(key, value, _format, _meta):
  if key == "RawInline":
    [format, source] = value
    imageSource = getAttribute(source, 'img', 'src')
    if imageSource:
      imageSource = os.path.normcase(imageSource.replace('\\', '/'))
      alt = getAttribute(source, 'img', 'alt')
      width = getAttribute(source, 'img', 'width')
      height = getAttribute(source, 'img', 'height')
      cw = getAttribute(source, 'img', 'cw')
      ch = getAttribute(source, 'img', 'ch')
      altObj = [Str(alt)] if alt else []
      attrObj = []
      if width:
        attrObj.append(['width', width])
      if height:
        attrObj.append(['height', height])
      if cw:
        attrObj.append(['cw', cw])
      if ch:
        attrObj.append(['ch', ch])
      return Image(['',[],attrObj],altObj,[imageSource, ''])


def getAttribute(html, tag, attribute):
  reStr = r"<%s[^>]+%s\s*=\s*['\"]([^'\"]+)[^>]*>" % (tag, attribute)
  searchRe = re.search(reStr, html)
  if searchRe:
    return searchRe.group(1)
  else:
    return None


def processImageInTable(key, value, _format, _meta):
  if key == "Table":
    [caption, alignments, widths, headers, rows] = value
    columnCount = len(alignments)
    maxImages = 0
    for row in rows:
      images = 0
      for cell in row:
        for subCell in cell:
          if subCell['t'] == 'Plain':
            for content in subCell['c']:
              if content['t'] == 'Image':
                images += 1
      maxImages = max(images, maxImages)
    if maxImages == 0:
      return
    textColumnCount = max(columnCount - maxImages, 0)
    magicWidth = (960-(180*textColumnCount))//maxImages
    for row in rows:
      for cell in row:
        for subCell in cell:
          if subCell['t'] == 'Plain':
            for content in subCell['c']:
              if content['t'] == 'Image':
                [attr, _inline, _target] = content['c']
                hasWidth = False
                for item in attr[2]:
                  if item[0] == 'width':
                    hasWidth = True
                    break
                if not hasWidth:
                  attr[2].append(['width', str(magicWidth)])


def processMathTag(key, value, _format, _meta):
  if key == "Math":
    [fmt, code] = value
    if fmt['t'] == 'DisplayMath':
      return []
    searchRe = re.search(r'\s*\\tag\s*{(.+)}|\s*\\tag\s*(\d)', code)
    if searchRe != None:
      if searchRe.group(1):
        tagContent = searchRe.group(1).replace('$', '')
      else:
        tagContent = searchRe.group(2).replace('$', '')
      code = code.replace(searchRe.group(), '\\#(' + tagContent + ')')
      return Math(fmt, code)
    
    # sys.stderr.write(str(code)+'\n')


def processMathDoubleBackslash(key, value, _format, _meta):
  if key == 'Para':
    if len(value) == 1 and value[0]['t'] == 'Math':
      [fmt, code] = value[0]['c']
      if fmt['t'] == 'DisplayMath' and '\\\\' in code:
        res = code.split('\\\\')
        for re in res:
          if re.count('\\begin') != re.count('\\end'):
            return
        return list(map(lambda re : Para([Math(fmt, re)]), res))    


def processMathOverToFrac(key, value, _format, _meta):
  if key == "Math":
    [fmt, code] = value
    while '\\over' in code:
      code = convertOverToFrac(code)
    return Math(fmt, code)
    
    # sys.stderr.write(str(code))


def convertOverToFrac(code):
  index = code.find('\\over')
  if index == -1:
    return code
  
  left = index-1
  leftStart = left
  leftEnd = left
  count = 0

  while left >= 0:
    if left == 0:
      leftStart = left
      if code[left] == '{':
        count -= 1
      break

    if leftEnd == left:
      if code[left] == ' ':
        left -= 1
        leftStart = left
        leftEnd = left
        continue

    if code[left] == '{' and code[left-1] != '\\':
      count -= 1
    elif code[left] == '}' and code[left-1] != '\\':
      count += 1

    if count < 0:
      leftStart = left
      break

    left -= 1

  leftStr = code[leftStart:leftEnd+1]
  if count < 0:
    leftStr = leftStr + '}'
  else:
    leftStr = '{' + leftStr + '}'

  right = index + 5
  rightStart = right
  rightEnd = right
  count = 0
  while right < len(code):
    if right == len(code) - 1:
      rightEnd = right
      if code[right] == '}':
        count -= 1
      break

    if rightStart == right:
      if code[right] == ' ':
        right += 1
        rightStart = right
        rightEnd = right
        continue

    if code[right] == '}' and code[right-1] != '\\':
      count -= 1
    elif code [right] == '{' and code[right-1] != '\\':
      count += 1

    if count < 0:
      rightEnd = right
      break

    right += 1
  
  rightStr = code[rightStart:rightEnd+1]
  if count < 0:
    rightStr = '{' + rightStr
  else:
    rightStr = '{' + rightStr + '}'

  # print(code[leftStart:leftEnd+1])
  # print(leftStr)
  # print(code[rightStart:rightEnd+1])
  # print(rightStr)

  if count < 0:
    return code[:leftStart]+'{'+'\\frac'+leftStr+rightStr+'}'+code[rightEnd+1:]
  else:
    return code[:leftStart]+'\\frac'+leftStr+rightStr+code[rightEnd+1:]


if __name__ == "__main__":
  toJSONFilters([processImage, processImageInTable, processMathTag, processMathOverToFrac, processMathDoubleBackslash])
