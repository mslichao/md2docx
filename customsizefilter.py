from pandocfilters import toJSONFilter, toJSONFilters, Math, Para, Image, RawInline, Str
import sys
import re
import os


def processCustomImageSize(key, value, _format, _meta):
  if key == "Image":
    [attrs, _inline, _target] = value
    width = height = cw = ch = None
    for attr in attrs[2]:
      if attr[0] == 'width':
        width = attr[1]
      if attr[0] == 'height':
        height = attr[1]
      if attr[0] == 'cw':
        cw = attr[1]
      if attr[0] == 'ch':
        ch = attr[1]
    if not width and not height:
      if cw or ch:
        newAttrs = []
        if cw:
          newAttrs.append(['width', cw])
        if ch:
          newAttrs.append(['height', ch])
        attrs[2] = newAttrs


if __name__ == "__main__":
  toJSONFilters([processCustomImageSize])
