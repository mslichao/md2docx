from pandocfilters import toJSONFilter, toJSONFilters, Math, Para, Image, RawInline, Str, LineBreak
import sys
import re
import os


def processImage(key, value, _format, _meta):
  if key == "RawInline":
    [format, source] = value
    if source.startswith('<br'):
      return LineBreak()
    else:
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
        return Image(['',[],attrObj],altObj,[imageSource, 'fig:' if alt else ''])


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
    imageWithTitle = checkSpecialImageTitleFormat(columnCount, headers, rows)
    if imageWithTitle:
      return [Para([imageWithTitle])]
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


def checkSpecialImageTitleFormat(columnCount, headers, rows):
  if columnCount != 1:
    return

  if len(headers)  != 1 or len(headers[0]) != 1:
    return

  headerCell = headers[0][0]

  if headerCell['t'] != 'Plain':
    return

  if len(headerCell['c']) != 1:
    return
  
  imageCell = headerCell['c'][0]

  if imageCell['t'] != 'Image':
    return

  image = imageCell['c']

  if len(rows) != 1 or len(rows[0]) != 1 or len(rows[0][0]) != 1:
    return

  rowCell = rows[0][0][0]

  if rowCell['t'] != 'Plain':
    return
  
  if len(rowCell['c']) == 0:
    return

  title = rowCell['c']

  if 'Image (' in str(title):
    return

  [_1, inline, target] = image
  inline.clear()
  inline.extend(title)
  target[1] = 'fig:'

  # sys.stderr.write(str(image)+'\n\n')
  # sys.stderr.write(str(title)+'\n\n')

  return imageCell

  
def processMathTag(key, value, _format, _meta):
  if key == "Math":
    [fmt, code] = value
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
      if '\\\\' in code:
        if fmt['t'] == 'DisplayMath':
          res = code.split('\\\\')
          for item in res:
            if item.count('\\begin') != item.count('\\end'):
              return
          return list(map(lambda item : Para([Math(fmt, item)]), res))
  elif key == 'Math':
    [fmt, code] = value
    if '\\\\' in code:
      if fmt['t'] == 'InlineMath':
        res = list(filter(None, re.split(r'( *\\\\ *)', code)))
        mathlist = list(map(lambda item : LineBreak() if re.match(r'( *\\\\ *)', item) else Math(fmt, item), res))
        return mathlist


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
