#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
"""
# Color Suggesting Program
/*******************************
  110-111: Modifications necessary for GTK frontend (June 2-5, 2012)
  109: Okay, that only took one day. Version 3.0 - Finished January 31, 2012
  096: Began porting from C++ to Python (January 31, 2012)
 * Version 2.0 - Finished June 30, 2009
 * 095:  Added source comments! Made some tweaks and cleaned up code.
 * 094: Added hue filter and range, luminosity algorithm, and xml sorter.
 * Version 1.0 - July 4, 2008
...
  This program is Public Domain. In places where there is no PD, this program is released under
  a Creatiuve Commons 0 license. In places where that is not honored, this program is released
  under the following license terms:
  Permission is granted to all persons to use, modify, redistribute, display, and in all other ways
  derive benefit from this program with or without recognition of its original author, without cost,
  worldwide, in perpetuity.
...
 * There are places where this code is not optimal. This is left as an exercise for the reader.
 * This program was written on a machine running Debian Etch and Lenny and Apache2 2.2.9-10+lenny2
 * It may compile on a Win32 machine, as well. It requires Apache2 or another HTTP daemon to run,
 * or possibly an environment containing the appropriate CONTENT_LENGTH variable and stdin input.
 *
 * Enjoy.
 */
"""

from math import (fabs, pow)
from operator import itemgetter
import codecs
from lumgrid import lumlib
import os

# CLEARBUF() char ch; while ((ch = getchar()) != '\n' and ch != EOF);
# /* Luminance contribution multipliers */
RLUM = 0.2126
GLUM = 0.7152
BLUM = 0.0722
# /* individual luminance cutoff */
LCUT = 0.03928
# /* After this many matching (displayed) colors, abort */
MAXMATCHES = 4000
MAXSORTED = 2500
BUILD = "111"
MSTACK = []
OUTPUT = "cli"

def sanityCheck(r,g,b, verbose = 1):
  """Given three integer values (red,blue,green), this function checks
  for unsane combinations that would result in excessive testing loops
  that yield unusable results. returns adjusted increment.
  """
  load = 0
  # In the middle is okay. At one end means about half the calculations will be wasted.
  if r < 85 or r > 170: load += 1
  if g < 85 or g > 170: load += 1
  if b < 85 or b > 170: load += 1
  if load > 2:
    if verbose: print "<div class=\"bad\">Sanity check override activated! Your color #%02X%02X%02X may not be tested against all 256^3 colors. WebSmart colors will be checked.</div>\n" % (r,g,b)
    return 17
  else:
    return 1

def getLargest(a,b):
  """Just what it says on the tin. Given two integers, returns the larger one."""
  if a > b:
    return a
  else:
    return b

def diff(x,y):
  """Given two integers, returns the difference between them."""
  return fabs(x - y)

def chkHue(r,g,b,h):
  """Given three component values and a hue type, determines if the RGB
  triplet represents a color of that hue type. Returns true or false.
  Hues are:
    0: no preference
    1: reds
    2: greens
    3: yellows
    4: blues
    5: magentas
    6: cyans
    7: grays/greys
    8: no preference, but instead of boolean return, give color's actual hue type as return
  """
  # Maximum difference between the two inputs that should be similar
  maxdiff = 35
  # Minimum difference between dominant/recessive input and the other two
  mingap = 4 * 17
  if h == 0: return True # No requested hue, all colors are good.
  if h == 1:
    if r > (getLargest(g,b) + mingap): # More red?
      return True
    else: return False
  if h == 2:
    if g > (getLargest(r,b) + mingap): # More green?
      return True
    else: return False
  if h == 3:
    if diff(r,g) < maxdiff and r > (b + mingap) and g > (b + mingap): # Less blue (yellows)?
      return True
    else: return False
  if h == 4:
    if b > (getLargest(g,r) + mingap): # More blue?
      return True
    else: return False
  if h == 5:
    if diff(r,b) < maxdiff and b > (g + mingap) and r > (g + mingap): # Less green (magentas)?
      return True
    else: return False
  if h == 6:
    if diff(b,g) < maxdiff and b > (r + mingap) and g > (r + mingap): # Less red (cyans)?
      return True
    else: return False
  if h == 7:
    if r == g and r == b: # Inputs equal (gray)?
      return True
    else: return False # h == 7 and hue not gray, or invalid hue passed. Display no colors.
  if h == 8:
    if r == g and r == b: # Inputs equal (gray)?
      return 7
    if diff(r,b) < maxdiff and b > (g + mingap) and r > (g + mingap): # Less green (magentas)?
      return 5
    if diff(b,g) < maxdiff and b > (r + mingap) and g > (r + mingap): # Less red (cyans)?
      return 6
    if diff(r,g) < maxdiff and r > (b + mingap) and g > (b + mingap): # Less blue (yellows)?
      return 3
    if r > (getLargest(g,b) + mingap): # More red?
      return 1
    if g > (getLargest(r,b) + mingap): # More green?
      return 2
    if b > (getLargest(g,r) + mingap): # More blue?
      return 4
    return 0 # can't happen, but just in case...
  return False # invalid hue

def getBrightness(r,g,b):
  """Given three component values, returns the brightness of the
  color. (float)
  """
  # ((Red value X 299) + (Green value X 587) + (Blue value X 114)) / 1000
  return ((r * 299) + (g * 587) + (b * 114)) / 1000

def getContrast(r1,g1,b1,r2,g2,b2):
  """Given six values representing two component triplets, returns the
  contrast between the two colors represented. (int)
  """
  # (maximum (Red value 1, Red value 2) - minimum (Red value 1, Red value 2)) + (maximum (Green value 1, Green value 2) - minimum (Green value 1, Green value 2)) + (maximum (Blue value 1, Blue value 2) - minimum (Blue value 1, Blue value 2))
  return int(diff(r1,r2) + diff(g1,g2) + diff(b1,b2))

def storeGoodColors(r,g,b,lumratio):
  """Given three ints and a float, stores the color represented and the ratio
  of its luminosity to the base color in a tuple and returns it for easy
  printing. (tuple)
  """
  a = "%02X%02X%02X" % (r,g,b)
  c = (a,lumratio)
  return c

def commonList(lista,listb):
  common = []
  for x in lista:
    if x in listb:
      common.append(x)
  return common

def storeLumRatios(rr,gg,bb,nr,ng,nb,nratio):
  global lumlib
  a = "%02X%02X%02X" % (rr,gg,bb)
  b = "%02X%02X%02X" % (nr,ng,nb)
  (c,d) = sorted((str(a),str(b)))
  try:
    lumlib[str(c)][str(d)] = str(nratio)[:7]
  except KeyError:
    try:
      lumlib[str(c)] = {}
      lumlib[str(c)][str(d)] = nratio
    except KeyError:
      return 1
  return 0

def savelumlib():
  global lumlib
  finaloutput = "lumlib = {out}\n".format(out = lumlib)
  fn = os.path.join(os.path.abspath("./lumgrid.py"))
  try:
    with codecs.open(fn,'wU','UTF-8') as f:
      f.write(finaloutput)
      f.close()
  except IOError as e:
    message = "The file %s could not be saved: %s" % (fn,e)
    print "?%s" % message
    return False
  return True


def sayGoodColors(given,match,ok,good):
  """Given string, a tuple (string,ratio), a minimum ratio, and a
  preferred ratio, prints the XHTML required to display them. (no return)
  """
  if match[1] >= good:
    print "\n<div class=\"pair b1\" ",
  elif match[1] >= ok:
    print "\n<div class=\"pair b2\" ",
  else:
    print  "\n<div class=\"pair b3\" ",
  print "title=\"{ratio:.3f}:1\"><div class=\"unit\" style=\"color: ".format(ratio = match[1]),
  print "#{one}; background-color: #{two};\">#{one}".format(one = given, two = match[0]),
  print "</div><div class=\"unit\" style=\"color: ",
  print "#{one}; background-color: #{two};\">#{one}".format(one = match[0], two = given),
  print "</div></div>"

def parrot(filename):
  """Given a filename, prints the contents of the file."""
  try:
    with codecs.open(filename,'rU','utf-8') as f:
      print f.read()
      f.close()
  except Exception as e:
    print " Could not print file: %s" % e

def stringTo(h):
  """Given a hex string, returns the decimal value in an integer."""
  d = [0,0]
  h = h[:2] # We only do numbers exactly two places.
  for i in range(len(h)):
    if "abcdefABCDEF0123456789".find(h[i]) != -1:
      d[i] = int(h[i],16)
    else:
      return None
  return (d[0] * 16) + d[1]

# /* ================================ Start WCAG2 Section ================================== */
def lum(rr,gg,bb):
  """Given three component values, returns the luminosity of the color. (float)"""
  rs = rr / 255.00 # Divide each input by 255.
  gs = gg / 255.00
  bs = bb / 255.00
  rl = 0.00; gl = 0.00; bl = 0.00
  #  I don't know what these formulae mean; they came from the WCAG2 guidelines.
  if rs <= LCUT:
    rl = rs / 12.92
  else:
    rl = pow((( rs + 0.055) / 1.055 ),2.4)
  if gs <= LCUT:
    gl = gs / 12.92
  else:
    gl = pow((( gs + 0.055) / 1.055 ),2.4)
  if bs <= LCUT:
    bl = bs / 12.92
  else:
    bl = pow((( bs + 0.055) / 1.055 ),2.4)
  return (RLUM * rl) + (GLUM * gl) + (BLUM * bl)

def lumrat(l1,l2):
  """Given two luminosity values (floats), returns the ratio of the
  larger to the smaller. (float)
  """
  l1 += 0.05 # to prevent dividing by zero
  l2 += 0.05 # same here
  ratio = 0.00
  if l1 > l2: # divide larger by smaller
    ratio = l1/l2
  else:
    ratio = l2/l1
  return ratio
# /* ================================== End WCAG2 Section ================================== */

def isValid(h):
  """Given a hexadecimal character, returns True if the character is a
  hex digit, False if it is not.
  """
  if len(h) > 1:
    print "Single character only, please, to isValid()."
    return False
  if "1234567890aAbBcCdDeEfF".find(h) != -1:
    return True
  else:
    return False

def valColor(color):
  """Given a color in the form of a string (#)R(R)G(G)B(B), returns a valid 6-character string RRGGBB, or None if length is not 3 or 6."""
  if color[0] == '#': # Trim leading hash, if present
    color = color[1:]
  if len(color) == 3: # How long was the input color? Some day, I ought to check if it's 3 and make it convert that to 6, like browsers do.
    color = color[0] + color[0] + color[1] + color[1] + color[2] + color[2]
  if len(color) != 6: # Invalid color code length. Color code must be 6 or 3 characters.
    color = None
  else:
    for i in range(6):
      if isValid(color[i]):
        goOn = True
      else:
        message = "Only hexadecimal digits are valid! (0-9, a-f)"
        if OUTPUT == "cgi": print message
        MSTACK.append(message)
        color = None
        i = 7
      i += 1
  return color

def valMinMax(minr,ming,minb,maxr,maxg,maxb):
  """Given minimums (3 ints) and maximums (3 ints) for Red, Green, and Blue,
  respectively, returns a tuple of the same values, validated and adjusted for
  error (e.g., max<min)."""
  if minr < 0: minr = 0 # If the minimum is less than zero, silly user, 0 is the bottom!
  if maxr < minr: maxr = minr # If the max is less than the minimum, silly user, minimum is the minimum!
  if maxr > 255: maxr = 255 # If the maximum is more than 255, silly user, 255 is the top!
  maxr += 1 # Increase the maximum by one, so we'll include the max in our tests
  if ming < 0: ming = 0 # Silly user, 0 is the bottom!
  if maxg < ming: maxg = ming # Silly user, check minimum and maximum in your dictionary!
  if maxg > 255: maxg = 255 # Silly user, 255 is the top!
  maxg += 1 # For test if (x>=max)
  if minb < 0: minb = 0 # Silly user, we can't start below 0!
  if maxb < minb: maxb = minb # Silly user, max must be greater than min!
  if maxb > 255: maxb = 255 # Silly user, there are no colors above 255!
  maxb += 1 # One for the road, please.
  return (minr,ming,minb,maxr,maxg,maxb)

def contLevels(sizeType):
  """Given a sizeType value (char), returns a tuple of the bare minimum and
  easy-to-read minimum as two floats."""
  if sizeType == 'h': # ...it's going to be header text, 18 or bigger.
    cM = 3.0
    cG = 3.5 # Minimum display and good values for header text 
  elif sizeType == 'b': # ...it's going to be between 14 and 18, or bold text.
    cM = 3.0
    cG = 4.5 # Minimum display and good values for bold or medium text
  elif sizeType == 'n': # ...it's going to be normal body copy, 14 or smaller.
    cM = 4.5
    cG = 5.0 # Minimum display and good values for normal text.
  else: # ...we want enhanced contrast (any size text) sizeType == 'e'.
      # ...or the user tried to send us something we didn't expect, so poo on them.
    cM = 5.0
    cG = 7.0 # Minimum display and good values for enhanced contrast at any size!
  return (cM,cG)

def unStringColor(color):
  """Given a valid 6-character hexcode, returns a tuple of three ints
  representing RGB values."""
  rr = stringTo(color[:2])
  gg = stringTo(color[2:4])
  bb = stringTo(color[4:6])
#    print "Your color: " + str(rr) + "," + str(gg) + "," + str(bb) + "."
  return (rr,gg,bb)

def colorVitals(rr,gg,bb):
  """Given three ints for red, green, and blue values, returns a tuple of the
  given color's brightness, contrast with black, contrast with white, and
  luminosity."""
  colorbrightness = getBrightness(rr,gg,bb) # How bright is the given color?
  cont0 = getContrast(rr,gg,bb,0,0,0) # How much does this color contrast with black?
  contf = getContrast(rr,gg,bb,255,255,255) # How much does this color contrast with white?
  givenLum = lum(rr,gg,bb) # What is the color's luminosity?
  return (colorbrightness,cont0,contf,givenLum)

def getLoops(minr,ming,minb,maxr,maxg,maxb,inc):
  """Given 6 ints for minimum RGB and maximum RGB and one int for the increment,
  returns a tuple of three lists containing every value the checker will loop
  through."""
  r = []
  g = []
  b = []
  ib = minb
  while ib < maxb:
    b.append(ib)
    ib += inc
  ig = ming
  while ig < maxg:
    g.append(ig)
    ig += inc
  ir = minr
  while ir < maxr:
    r.append(ir)
    ir += inc
  return (r,g,b)

def main(): # The main event
  """This function is run when called from the shell, of course."""
  print "Content-Type: text/html\n\n"

  goOn = False
  cM = 5.0 # Minimum contrast ratio
  cG = 7.0 # Good contrast ratio
  cD = 0 # How many colors will we display?
  colorMatches = 0 # How many accessible colors will we find?
  rr = 0 # We'll break it down into red,
  gg = 0                               # green,
  bb = 0                                      # and blue.
  inc = 17; hue = 0; minr = 0; ming = 0; minb = 0; maxr = 255; maxg = 255; maxb = 255; sizeType = 'n'
  color = ""
  colors = []
  parrot("color1.htf")
  print "<h1>DAOS color suggestion CGI program</h1><p class=\"r\">Build %s</p><p>Looking for color input... " % BUILD
  # Grab GET data from URL
  query = cgi.FieldStorage()
  if len(query) == 0: # What is this? No input?
    print "finding none; user input requested:</p>" #  Guess I'll tell the user (s)he needs to give me some input.
    parrot("colorask.htf") # Print the form.
    goOn = False
  else:
    print "</p><p>Checking data..." # <!-- %s -->",query); # Tell the user we're doing something
    color = query.getvalue("color",None)
    # check if color is len 3 and expand it like browsers do.
    method = int(query.getvalue("cm","1")) # Method to decide if colors are accessible (default WCAG2)
    inc = int(query.getvalue("iv","17")) # Increment of values to test (default is WebSmart colors)
    hue = int(query.getvalue("cp","0")) # Requested hue type (default any)
    minr = int(query.getvalue("minr","0")) # Minimum value of red to test against given color
    ming = int(query.getvalue("ming","0")) # Minimum value of green to test against given color
    minb = int(query.getvalue("minb","0")) # Minimum value of blue to test against given color
    maxr = int(query.getvalue("maxr","255")) # Maximum value of red to test against given color
    maxg = int(query.getvalue("maxg","255")) # Maximum value of green to test against given color
    maxb = int(query.getvalue("maxb","255")) # Maximum value of blue to test against given color
    sizeType = query.getvalue("sz",'n')[:1] # We only care about the first character, no matter what the browser sent us.
    color = valColor(color)
    if color is None:
      print "</p>"
      parrot("colorask.htf") # Print the form.
      goOn = False
    else:
      goOn = True
      print "." # Let the user know we're doing something
      (minr,ming,minb,maxr,maxg,maxb) = valMinMax(minr,ming,minb,maxr,maxg,maxb)
      # Based on the character 'sizeType'...
      (cM,cG) = contLevels(sizeType)
  print "</p>\n"
  if goOn:
    (rr,gg,bb) = unStringColor(color)
    if method == 2: inc = 51 # Method 2 always displays every color, so we'll only do it with the WebSafe colorspace.
    if inc == 1: inc = sanityCheck(rr,gg,bb) #  If we're testing all colors, decide if this is something a sane person would do.
    print "<p>Using increments of {0}...".format(inc),
    if hue != 0: # Looking at hue...
      print "limited to ",
      if hue == 1: print "reddish hues.",
      elif hue == 2: print "greenish hues.",
      elif hue == 3: print "yellowish hues.",
      elif hue == 4: print "bluish hues.",
      elif hue == 5: print "magentine hues.",
      elif hue == 6: print "cyanate hues.",
      elif hue == 7: print "grays.",
      else: print "all hues.",
    print " Color range used is r:{0}-{1}/g:{2}-{3}/b:{4}-{5}.</p>".format(minr,maxr - 1,ming,maxg - 1,minb,maxb - 1), # Tell user about requested (or corrected) color ranges.
    goOn = False; # Don't continue... unless the next test passes.
    print "<p class=\"yourcolor\" style=\"border-color: #{0};\">Color entered: R: {1} G: {2} B: {3} (#{0})</p>".format(color, rr,gg,bb) # Remind user of the given color. It's been so long, I almost forgot.
    (colorbrightness,cont0,contf,givenLum) = colorVitals(rr,gg,bb)
    print "<p>Color has a brightness of <strong>" + str(colorbrightness) + "</strong>",
    print " and a luminance of <em>{0:.2%}</em>.".format(givenLum),
    print " Its contrast with black is <strong>" + str(cont0) + "</strong>, and its contrast with white is <strong>" + str(contf) + "</strong>.</p>" # The user might be interested in this information. Tell the user what we've learned.
    (rloop,gloop,bloop) = getLoops(minr,ming,minb,maxr,maxg,maxb,inc)
    for nr in rloop: #Red loop: Start at minr, stop at maxr, increment by inc every time around.
      for ng in gloop: #Green loop: Start at ming, stop at maxg, increment by inc every time around.
        for nb in bloop: #Blue loop: Start at minb, stop at maxb, increment by inc every time around.
          if chkHue(nr,ng,nb,hue): # Is the color we're testing of the proper hue type?
            nLum = lum(nr,ng,nb) # Luminance of the tested color is what?
            nratio = lumrat(givenLum,nLum) # Ratio of tested luminance vs. given color's luminance is what?
            if method == 0: # Use the old contrast/Brightness method (deprecated)
              nBright = getBrightness(nr,ng,nb) # Check out the brightness of this color.
              brightDiff = fabs(nBright - colorBrightness) # How different is it?
              if brightDiff > 125: # diff in bright should be greater than 125
                contrast = getContrast(rr,gg,bb,nr,ng,nb) # Oh, check the contrast between these two colors
                if contrast > 500: # contrast should be greater than 500
                  colors.append(storeGoodColors(nr,ng,nb,nratio))
                  cD += 1; colorMatches += 1
            elif nratio >= cM or method == 2: # Is the color match good enough to display?
              colors.append(storeGoodColors(nr,ng,nb,nratio))
              cD += 1
              if nratio >= cG: # Is the color match a preferable match?
                colorMatches += 1
          if cD >= MAXMATCHES: # If we have a lot of colors to display...
            bloop = []
            print "<p class=\"bad clr\">Maximum matches (" + str(MAXMATCHES) + ") reached. Aborting process to save server resources!</p>" # Tell the user that there were too many.
            break
          if colorMatches >= MAXSORTED and method == 3: # If we have a lot of colors to sort...
            bloop = []
            print "<p class=\"bad clr\">Maximum sorted matches (" + str(MAXSORTED) + ") reached. Aborting process to prevent browser spinning!</p>"
            break
      goOn = True
#    print colors
  # else:
  #   print "I received: " + color
  if goOn:
    if method == 3:
      colors = sorted(colors,key=itemgetter(1), reverse = True)
    for m in colors:
      sayGoodColors(color,m,cM,cG)
    print "<p style=\"clear: left;\">Color #{0} has {1} good matches in the range of ".format(
      color,colorMatches), # Tell the user how many matches were found.
    case = {}
    case['1'] = "all"
    case['17'] = "Web smart"
    case['51'] = "WebSafe"
    print "{0} colors.</p>".format(case[str(inc)])
  # else:
    # print "An error occurred during processing."
  print "<p class=\"extra\">DAOS (Don&#039;t Analyze Only, Suggest) color suggestion CGI program. Version Main 3.0 - Released January 31, 2012 (2.0 - Released July 4, 2009; 1.0 - Released July 4, 2008 to give freedom to Web designers by giving them suggestions when their color pairings don't work in an analyzer.)</p>" # Tell the user a little bit about this program. Lofty, isn't it?
  parrot("color2.htf")
  return 0

# Standard boilerplate to call the main()
if __name__ == '__main__':
  import cgi
  OUTPUT = "cgi"
  main()
