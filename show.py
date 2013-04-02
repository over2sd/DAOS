#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import color
from lumgrid import lumlib

def findCommon(keys):
  cM = 5.1
  commonfore = []
  try:
    commonfore = lumlib[keys[0]].keys()
  except KeyError:
    print "No data for %s. Please run daos to populate grid for this color. Grid uses 6-digit codes." % x
    return commonfore
  for lc in commonfore:
    if (float(lumlib[keys[0]][lc]) < cM):
      commonfore.remove(lc)
  for x in keys:
    comp = []
    try:
      comp = lumlib[x].keys()
    except KeyError:
      print "No data for %s. Please run daos to populate grid for this color. Grid uses 6-digit codes." % x
      return commonfore
    for lc in comp:
      if (float(lumlib[x][lc]) < cM):
        comp.remove(lc)
    commonfore = color.commonList(commonfore,comp)
  return commonfore

def magicSort(a,b):
  out = []
  sorting = []
  for c in a:
    sorting.append((str(c),lumlib[str(b)][str(c)]))
  sorting = sorted(sorting,key = lambda x:x[1])
  for d in sorting:
    out.append(d[0])
  return out

def main():
  colors = ["007700","550000","000055","FFFF00","BBFFCC","FFFFFF"]
  bgcols = ["007700","000055","550000"]
#  bgcols = ["009999","ffff00"]
  color.parrot("color1.htf")
  print "<table>"
  (cM,cG) = color.contLevels('n')
  for i in colors:
    (rr,gg,bb) = color.unStringColor(i)
    (colorbrightness,cont0,contf,givenLum) = color.colorVitals(rr,gg,bb)
    print "<tr>"
    a = '?'
    for j in colors:
      (nr,ng,nb) = color.unStringColor(j)
      nLum = color.lum(nr,ng,nb) # Luminance of the tested color is what?
      nratio = color.lumrat(givenLum,nLum) # Ratio of tested luminance vs. given color's luminance is what?

      if (nratio >= cM):
        if (nratio >= cG):
          a = '!'
        else:
          a = ''
        print "<td style=\"color: #{one}; background-color: #{two};\">#{one}/#{two}{bang}</td>".format(one = j,two = i,bang = a)
    print "</tr>"
  print "</table>"
  if len(bgcols) > 1:
    cf = findCommon(bgcols)
    cf = magicSort(cf,bgcols[0])
    for fc in cf:
      print "<div>"
      for bc in bgcols:
        (k1,k2) = sorted([str(bc).upper(),str(fc)])
        ratio = ''
        try:
          ratio = lumlib[k1][k2]
        except KeyError as e:
          print "Results unreliable."
          break
        print "<span style=\"font-family: monospace; color: #{fg}; background-color: #{bg};\">: {fg}/{bg}: {rat} :</span>".format(fg = fc,bg = bc,rat = ratio)
      print "</div>"
  color.parrot("color2.htf")
  return 0

if __name__ == "__main__":
  main()
