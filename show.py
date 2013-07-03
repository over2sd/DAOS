#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import color
from lumgrid import lumlib

def gridLums(c1,c2):
  cG = 5.1
  global lumlib
  (c1,c2) = sorted((str(c1),str(c2)))
  try:
    nratio = float(lumlib[str(c1)][str(c2)])
  except KeyError:
    (r1,g1,b1) = color.unStringColor(c1)
    (r2,g2,b2) = color.unStringColor(c2)
    l1 = color.lum(r1,g1,b1)
    l2 = color.lum(r2,g2,b2)
    nratio = color.lumrat(l1,l2)
    if nratio >= cG: color.storeLumRatios(r1,g1,b1,r2,g2,b2,nratio)
  return nratio

def findCommon(keys):
  cM = 5.1
  order = []
  tmp = []
  for x in range(len(keys)):
    try:
      tmp.append([x,len(lumlib[keys[x]].keys())])
    except KeyError as k: # TODO: Fix this so it doesn't keep analyzing colors with no higher pairings.
      print "Analyzing BG color %s..." % k
      (rloop,gloop,bloop) = color.getLoops(0,0,0,255,255,255,51) # all websafe colors only
      for nr in rloop: #Red loop: Start at minr, stop at maxr, increment by inc every time around.
        for ng in gloop: #Green loop: Start at ming, stop at maxg, increment by inc every time around.
          for nb in bloop: #Blue loop: Start at minb, stop at maxb, increment by inc every time around.
            nc = "%02X%02X%02X" % (nr,ng,nb)
            nratio = gridLums(keys[x],nc)
      try:
        tmp.append([x,len(lumlib[keys[x]].keys())])
      except KeyError:
        tmp.append([x,0])
  tmp = sorted(tmp,key = lambda y:y[1])
  for z in tmp:
    order.append(z[0])
#  print order
  commonfore = []
  for y in order:
    comp = []
    x = keys[y]
    try:
      comp = lumlib[x].keys()
      if commonfore == []:
        for i in comp:
          commonfore.append(str(i))
    except KeyError:
      print "Missing data for %s. Please run daos to populate grid for this color. Grid uses 6-digit codes." % x
      return commonfore
    for lc in comp:
      cA = 0.0
      try:
        cA = float(lumlib[x][lc])
      except KeyError:
        print "Missing data for %s." % x
        cA = gridLums(x,lc)
        return commonfore
      if (cA < cM):
        comp.remove(lc)
    commonfore = color.commonList(commonfore,comp)
  return commonfore

def magicSort(a,b):
  out = []
  sorting = []
  for c in a:
    nratio = gridLums(b,c)
    sorting.append((str(c),nratio))
  sorting = sorted(sorting,key = lambda x:x[1])
  for d in sorting:
    out.append(d[0])
  return out

def showOff(colors,bgcols):
  color.parrot("color1.htf")
  print "<p>Foreground colors being tried: "
  for c in colors:
    print "%s " % (c),
  print "</p><p>Backgrounds used for comparison: "
  for b in bgcols:
    print "%s " % (b),
  print "</p>"
  print "<table>"
  (cM,cG) = color.contLevels('n')
  for i in bgcols:
    print "<tr>"
    a = ''
    for j in colors:
      nratio = gridLums(i,j)
      if (nratio >= cG):
        a = 'cgood'
      elif (nratio >= cM):
        a = 'cmin'
      elif (i == j):
        a = 'cnone'
      else:
        a = 'cbad'
      print "<td class=\"{bang}\" style=\"color: #{one}; background-color: #{two};\">#{one}/#{two}</td>".format(one = j,two = i,bang = a)
    print "</tr>"
  print "</table>"
  if len(bgcols) > 1:
    cf = findCommon(bgcols)
    print "<p>Common foregrounds:</p>" # ??? May have messed this up somehow. Don't remember its original intent.
    cf = magicSort(cf,bgcols[0]) # Um, I guess sorted based on contrast with first given background? I should have documented this better.
    for fc in cf:
      print "<div class=\"holder\">"
      for bc in bgcols:
        (k1,k2) = sorted([str(bc).upper(),str(fc)])
        ratio = ''
        try:
          ratio = lumlib[k1][k2]
        except KeyError as e:
          ratio = gridLums(k1,k2)
          break
        if (ratio >= cG):
          a = ''
        elif (ratio >= cM):
          a = ' cmin'
        elif (fc == bc):
          a = ' cnone'
        else:
          a = ' cbad'
        print "<span class=\"comfg{con}\" style=\"font-family: monospace; color: #{fg}; background-color: #{bg};\"> {fg}/{bg}: {rat} </span>".format(fg = fc,bg = bc,rat = ratio,con = a)
      print "</div>"
  print "<p class=\"clr\">Size of grid: %i</p>" % len(lumlib)
  color.parrot("color2.htf")
  color.savelumlib()
  return 0

if __name__ == "__main__":
  import sys

  colors = ["111111","003333"]
  bgcols = ["CCFFCC","99CCFF"]
  opts = sys.argv[1:]
  for o in range(len(opts)):
    if (opts[o] == "-i"):
      from getcolors import parseFileList
      flist = []
      off = 0
      o += 1
      for p in opts[o:]:
        if (p.startswith("-")):
#          print o
          break
        else:
          o += 1
          flist.append(p)
#      print flist
      coldic = parseFileList(flist)
      colors = sorted(coldic['fg'])
      bgcols = sorted(coldic['bg'])
    elif (opts[o] == "-h"):
      print "  Usage:"
      print "%s - Uses internal list of colors" % sys.argv[0]
      print "%s <file> - Reads colors from <file> (wildcards valid)" % sys.argv[0]
      sys.exit(0)
  showOff(colors,bgcols)
