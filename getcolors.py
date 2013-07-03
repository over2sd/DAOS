#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import re

def stripColors(fn):
  try:
    f = open(fn,'r')
    check = re.compile("([a-zA-Z-]+): .*?(#[\dabcdefABCDEF][\dABCDEFabcdef][\dABCDEFabcdef]+);?")
    matches = []
    colors = {}
    for s in f:
      t = s.split(";")
      for s in t:
        m = check.findall(s)
#        print m
        for n in m: matches.append("%s: %s" % (n[0],n[1]))
    f.close()
  except Exception as e:
    print "Error: %s" % e
    return {}
#  print matches
  colors['fg'] = []
  colors['bg'] = []
  colors['border'] = []
  suf = ": .*?(#[\dabcdefABCDEF][\dABCDEFabcdef][\dABCDEFabcdef]+);?"
  for t in [("(background-)?color","fg"),("background(-color)?","bg"),("border(-color)?","border")]:
    check = re.compile("%s%s" % (t[0], suf))
    for line in matches:
      m = check.search(line)
      if (m and t[1] == "fg"):
#        print "? %s" % m.group(0)
        bg = re.search("^background-",m.group(0))
        if bg: m = None
      if m: m = re.search("#[\dabcdefABCDEF][\dABCDEFabcdef][\dABCDEFabcdef]+",m.group(0))
      if m:
#        print "%s: %s (%s)" % (t[1],m.group(0),line)
        c = len(m.group(0))
        if c not in [4,7]:
          print "Invalid color found in CSS! (%s)" % m.group(0)
        else:
          if c == 7: c = m.group(0)[1:]
          elif c == 4:
            m = m.group(0)
            c = m[1] + m[1] + m[2] + m[2] + m[3] + m[3]
          if c not in colors[t[1]]:
            colors[t[1]].append(c)
  return colors

def pushCols(old,new):
  try:
    for k in new.keys():
        try:
          x = old[k]
        except KeyError:
          old[k] = []
        for i in new[k]:
          if (i not in old[k]):
            old[k].append(i)
  except KeyError:
    print "Empty"
    pass
  return old

def parseFileList(lof):
  allcols = {}
  allcols['border'] = []
  allcols['bg'] = []
  allcols['fg'] = []
  for f in range(len(lof)):
    if __name__ == "__main__": print "Processing %s" % lof[f]
    cdic = stripColors(lof[f])
    allcols = pushCols(allcols,cdic)
    if __name__ == "__main__": print cdic
  return allcols

if __name__ == "__main__":
  import sys
  allcols = {}
  allcols['border'] = []
  allcols['bg'] = []
  allcols['fg'] = []
  s = ""
  if (len(sys.argv) > 2):
    s ="s"
  else:
    s = " %s" % sys.argv[1]
  if (len(sys.argv) <= 1):
    print "Please supply a filename."
  else:
    allcols = parseFileList(sys.argv[1:])
    print "\nAll colors used in file%s:" % (s)
    print "Borders: ",
    for c in sorted(allcols['border']):
      print "%s " % (c),
    print "\nBackgrounds: ",
    for c in sorted(allcols['bg']):
      print "%s " % (c),
    print "\nForegrounds: ",
    for c in sorted(allcols['fg']):
      print "%s " % (c),
    print "\n"
