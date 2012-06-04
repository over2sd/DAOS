#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk
from operator import itemgetter

import color

BUILD = 59
version = "3.5"
LINESTACK = []
MAXMATCHES = 4000
MAXSORTED = 2500
colors = []
status = gtk.TextBuffer()
statuswindow = gtk.TextView(status)

def buildUI(self,bb):
  vb = gtk.VBox()
  vb.show()
  sw = gtk.ScrolledWindow()
  sw.set_policy(gtk.POLICY_NEVER,gtk.POLICY_AUTOMATIC)
  sw.show()
  sw.add_with_viewport(vb)
  self.pack_start(sw,1,1,2)
  row = gtk.HBox()
  say(0,".")
  row.show()
  label = gtk.Label("Base Color:")
  label.show()
  row.pack_start(label,0,0,4)
  c = gtk.Entry(7)
  c.set_text("#000")
  c.show()
  colex = gtk.Entry(0)
  colex.set_can_focus(False)
  colex.show()
  setBack(None,colex,c)
  b = gtk.Button("Choose Color")
  b.connect("clicked",selColor,c,colex)
  b.show()
  row.pack_start(c,0,0,4)
  row.pack_start(b,0,0,4)
  row.pack_start(colex,0,0,4)
  c.connect("changed",setBack,colex,c)
  vb.pack_start(row,0,0,4)
  row = gtk.HBox()
  say(0,".")
  row.show()
  label = gtk.Label("Contrast Filter:")
  label.show()
  row.pack_start(label,0,0,4)
  cm = gtk.combo_box_new_text()
  choices = ["WCAG2","Unfiltered (show luminosity ratios)","WCAG2 sorted by luminosity"]
  for x in choices:
    cm.append_text(x)
  cm.set_active(0)
  cm.show()
  row.pack_start(cm,0,0,4)
  vb.pack_start(row,0,0,4)
  row = gtk.HBox()
  say(0,".")
  row.show()
  label = gtk.Label("Colorspace:")
  label.show()
  row.pack_start(label,0,0,4)
  adj = gtk.Adjustment(1,1,255,1,10)
  iv = gtk.SpinButton(adj)
  iv.show()
  cs = gtk.combo_box_new_text()
  choices = ["WebSafe","WebSmart","All (Generates huge lists - Use w/extreme caution!)"]
  for x in choices:
    cs.append_text(x)
  cs.set_active(1)
  cs.show()
  cs.connect("changed",setFromCombo,iv.set_value,[51,17,1])
  setFromCombo(cs,iv.set_value,[51,17,1])
  row.pack_start(cs,0,0,4)
  row.pack_start(iv,0,0,4)
  vb.pack_start(row,0,0,4)
  row = gtk.HBox()
  say(0,".")
  row.show()
  label = gtk.Label("Hue Filter:")
  label.show()
  row.pack_start(label,0,0,4)
  cp = gtk.combo_box_new_text()
  choices = ["No Filter","Reds","Greens","Yellows","Blues","Magentas","Cyans","Grays"]
  for x in choices:
    cp.append_text(x)
  cp.set_active(0)
  cp.show()
  row.pack_start(cp,0,0,4)
  vb.pack_start(row,0,0,4)
  row = gtk.HBox()
  say(0,".")
  row.show()
  label = gtk.Label("Hue Range:")
  label.show()
  row.pack_start(label,0,0,4)
  t = gtk.Table(3,4,True)
  t.show()
  adj = gtk.Adjustment(0,0,255,1,10)
  nr = gtk.SpinButton(adj)
  nr.show()
  t.attach(nr,1,2,2,3)
  adj = gtk.Adjustment(255,0,255,1,10)
  xr = gtk.SpinButton(adj)
  xr.show()
  t.attach(xr,1,2,1,2)
  label = gtk.Label("Red")
  label.show()
  t.attach(label,1,2,0,1)
  adj = gtk.Adjustment(0,0,255,1,10)
  ng = gtk.SpinButton(adj)
  ng.show()
  t.attach(ng,2,3,2,3)
  adj = gtk.Adjustment(255,0,255,1,10)
  xg = gtk.SpinButton(adj)
  xg.show()
  t.attach(xg,2,3,1,2)
  label = gtk.Label("Green")
  label.show()
  t.attach(label,2,3,0,1)
  adj = gtk.Adjustment(0,0,255,1,10)
  nb = gtk.SpinButton(adj)
  nb.show()
  t.attach(nb,3,4,2,3)
  adj = gtk.Adjustment(255,0,255,1,10)
  xb = gtk.SpinButton(adj)
  xb.show()
  t.attach(xb,3,4,1,2)
  label = gtk.Label("Blue")
  label.show()
  t.attach(label,3,4,0,1)
  label = gtk.Label("Min")
  label.show()
  t.attach(label,0,1,2,3)
  label = gtk.Label("Max")
  label.show()
  t.attach(label,0,1,1,2)
  row.pack_start(t,1,1,4)
  vb.pack_start(row,0,0,4)
  row = gtk.HBox()
  say(0,".")
  row.show()
  label = gtk.Label("Text Type (for WCAG2 only): (size;good,min):")
  label.show()
  row.pack_start(label,0,0,4)
  tt = gtk.combo_box_new_text()
  choices = ["Header (*>=18; 3.5,3)","Bold (14<*<18; 4.5,3)","Normal (*<=14; 5,4.5)","Enhanced Contrast (*;7, 5)"]
  for x in choices:
    tt.append_text(x)
  tt.set_active(2)
  tt.show()
  row.pack_start(tt,0,0,4)
  sz = gtk.Entry(1)
  sz.set_width_chars(1)
  sz.set_sensitive(False)
#  cm.show()
  tt.connect("changed",setFromCombo,sz.set_text,['h','b','n','e'])
  setFromCombo(tt,sz.set_text,['h','b','n','e'])
  row.pack_start(sz,0,0,4)
  vb.pack_start(row,0,0,4)
  label = gtk.Label("Color Output")
  label.show()
  vb.pack_start(label,0,0,1)
  colbox = gtk.VBox()
  say(0,".")
  colbox.show()
  vb.pack_start(colbox,0,0,4)
  pb = gtk.Button("Start")
  say(0,".")
  pb.show()
  bb.pack_start(pb,0,0,4)
  pb.connect("clicked",triggerProcess,c,nr,ng,nb,xr,xg,xb,iv,sz,cm,cp,colbox)
  return

def compileColors(c,minr,ming,minb,maxr,maxg,maxb,inc,sizeType,**kwargs):
  """Given all inputs, compiles a list of tuples containing colors that work as
  backgrounds to the chosen color. Returns this list.
  Inputs:
    A color code (string)
    Six ints (ming R/G/B, max R/G/B)
    An increment (int)
    a size tyoe for setting the minimum contrasts (char)
    Keyword args:
      method: 0 - Legacy method C/B, 1 - WCAG, 2 - WCAG/sortbylum, 3 - Unfiltered
      hue requirement (int):
        0: all hues
        1: reddish hues
        2: greenish hues
        3: yellowish hues
        4: bluish hues
        5: magentine hues
        6: cyanate hues
        7: grays
  """
  global colors
  hue = '0'
  method = '1'
  goOn = False
  cM = 5.0 # Minimum contrast ratio
  cG = 7.0 # Good contrast ratio
  cD = 0 # How many colors will we display?
  colorMatches = 0 # How many accessible colors will we find?
  rr = 0 # We'll break it down into red,
  gg = 0                               # green,
  bb = 0                                      # and blue.
  colors = []
  for key in kwargs:
    if key == "method": method = str(kwargs[key])
    if key == "hue": hue = str(kwargs[key])

  c = color.valColor(c)
  if c is None:
    say(0,"Invalid color!\n")
    goOn = False
  else:
    goOn = True
    (minr,ming,minb,maxr,maxg,maxb) = color.valMinMax(minr,ming,minb,maxr,maxg,maxb)
    # Based on the character 'sizeType'...
    (cM,cG) = color.contLevels(sizeType)
  say(0,"...")
  if goOn:
    (rr,gg,bb) = color.unStringColor(c)
    if method == '2': inc = 51 # Method 2 always displays every color, so we'll only do it with the WebSafe colorspace.
    if inc == 1: inc = color.sanityCheck(rr,gg,bb) #  If we're testing all colors, decide if this is something a sane person would do.
    say(1,"Using increments of {0}...".format(inc))
    if hue != '0': # Looking at hue...
      say(1,"limited to ")
      hues = ""
      if hue == '1': hues = "reddish hues."
      elif hue == '2': hues = "greenish hues."
      elif hue == '3': hues = "yellowish hues."
      elif hue == '4': hues = "bluish hues."
      elif hue == '5': hues = "magentine hues."
      elif hue == '6': hues = "cyanate hues."
      elif hue == '7': hues = "grays."
      else: hues = "all hues."
      say(0,hues + "\n")
    say(0," Color range used is r:{0}-{1}/g:{2}-{3}/b:{4}-{5}.\n".format(minr,maxr - 1,ming,maxg - 1,minb,maxb - 1)) # Tell user about requested (or corrected) color ranges.
    goOn = False; # Don't continue... unless the next test passes.
#    say(0,"<p class=\"yourcolor\" style=\"border-color: #{0};\">Color entered: R: {1} G: {2} B: {3} (#{0})</p>".format(c, rr,gg,bb) # Remind user of the given color. It's been so long, I almost forgot.
# Replace below with GTK fanciness to show colored stuff.
    say(0,"Color entered: R: {1} G: {2} B: {3} (#{0})\n".format(c, rr,gg,bb)) # Remind user of the given color. It's been so long, I almost forgot.
    (colorbrightness,cont0,contf,givenLum) = color.colorVitals(rr,gg,bb)
    say(1,"Color has a brightness of %s" % colorbrightness)
    say(1,"and a luminance of {0:.2%}.".format(givenLum))
    say(0,"Its contrast with black is %s, and its contrast with white is %s.\n" % (cont0,contf)) # The user might be interested in this information. Tell the user what we've learned.
    (rloop,gloop,bloop) = color.getLoops(minr,ming,minb,maxr,maxg,maxb,inc)
    for nr in rloop: #Red loop: Start at minr, stop at maxr, increment by inc every time around.
      for ng in gloop: #Green loop: Start at ming, stop at maxg, increment by inc every time around.
        for nb in bloop: #Blue loop: Start at minb, stop at maxb, increment by inc every time around.
          if color.chkHue(nr,ng,nb,int(hue)): # Is the color we're testing of the proper hue type?
            nLum = color.lum(nr,ng,nb) # Luminance of the tested color is what?
            nratio = color.lumrat(givenLum,nLum) # Ratio of tested luminance vs. given color's luminance is what?
            if method == '0': # Use the old contrast/Brightness method (deprecated)
              nBright = color.getBrightness(nr,ng,nb) # Check out the brightness of this color.
              brightDiff = color.fabs(nBright - colorBrightness) # How different is it?
              if brightDiff > 125: # diff in bright should be greater than 125
                contrast = color.getContrast(rr,gg,bb,nr,ng,nb) # Oh, check the contrast between these two colors
                if contrast > 500: # contrast should be greater than 500
                  colors.append(color.storeGoodColors(nr,ng,nb,nratio))
                  cD += 1; colorMatches += 1
            elif nratio >= cM or method == '2': # Is the color match good enough to display?
              colors.append(color.storeGoodColors(nr,ng,nb,nratio))
              cD += 1
              if nratio >= cG: # Is the color match a preferable match?
                colorMatches += 1
          if cD >= MAXMATCHES: # If we have a lot of colors to display...
            bloop = []
            say(0,"Maximum matches (" + str(MAXMATCHES) + ") reached. Aborting process to save CPU resources!\n") # Tell the user that there were too many.
            break
          if colorMatches >= MAXSORTED and method == '3': # If we have a lot of colors to sort...
            bloop = []
            say(0,"Maximum sorted matches (" + str(MAXSORTED) + ") reached. Aborting process to prevent browser spinning!\n")
            break
  print "."
  return colors

def displayColors(method,c,sz,box):
  global colors
  (cM,cG) = color.contLevels(sz)
  if method == 3:
    colors = sorted(colors,key=itemgetter(1), reverse = True)
  column = 0
  row = None
  for m in colors:
    if method == 2 or m[1] >= cM:
      if column == 0:
        row = gtk.HBox()
        row.show()
        box.pack_start(row,0,0,4)
      sayGoodColors(c,m,cM,cG,row)
      column += 1
      if column == 3:
        column = 0
  return

def say(hold,text,**kwargs):
  global status
  global statuswindow
  nospace = 0
  for key in kwargs:
    if key == "nospace": nospace = int(kwargs[key])
  if hold:
    LINESTACK.append(text)
  else:
    spc = ""
    while len(LINESTACK) > 0:
      status.insert_at_cursor("%s%s" % (spc,LINESTACK[0]))
      if len(LINESTACK[0]) > 0:
        if LINESTACK[0][-1] != ' ' and nospace == 0:
          spc = " "
        else:
          spc = ""
#      print "%s" % LINESTACK[0],
      del LINESTACK[0]
    status.insert_at_cursor("%s" % text)
#    print "%s" % text
    em = gtk.TextMark("end",False)
    status.add_mark(em,status.get_end_iter())
    statuswindow.scroll_to_mark(em,0.0)
    status.delete_mark(em)
  return

def sayGoodColors(given,match,ok,good,box):
  """Given string, a tuple (string,ratio), a minimum ratio, a preferred ratio,
  and a target, displays them in the target GTK container. (no return)
  """
  given = color.valColor(given)
  l1 = gtk.Entry(11)
  l1.set_width_chars(11)
  l1.set_has_frame(False)
  l1.set_text("#%s" % match[0])
  l2 = gtk.Entry(11)
  l2.set_width_chars(11)
  l2.set_has_frame(False)
  l2.set_text("#%s" % given)
  l1.set_can_focus(False)
  l1.set_can_focus(False)
  l1.show()
  l2.show()
  c1 = gtk.gdk.color_parse("#%s" % match[0])
  c2 = gtk.gdk.color_parse("#%s" % given)
  pair = gtk.HBox()
  pair.show()
  if match[1] >= good:
#    print "\n<div class=\"pair b1\" ",
    l1.set_text("* %s *" % l1.get_text())
    l2.set_text("* %s *" % l2.get_text())
  elif match[1] >= ok:
#    print "\n<div class=\"pair b2\" ",
    l1.set_text("  %s  " % l1.get_text())
    l2.set_text("  %s  " % l2.get_text())
  else:
#    print  "\n<div class=\"pair b3\" ",
    l1.set_text("( %s )" % l1.get_text())
    l2.set_text("( %s )" % l2.get_text())
  l1.set_tooltip_text("{ratio:.3f}:1".format(ratio = match[1]))
  l2.set_tooltip_text("{ratio:.3f}:1".format(ratio = match[1]))
#  print "title=\><div class=\"unit\" style=\"color: ",
#  print "#{one}; background-color: #{two};\">#{one}".format(one = given, two = match[0]),
#  print "</div><div class=\"unit\" style=\"color: ",
#  print "#{one}; background-color: #{two};\">#{one}".format(one = match[0], two = given),
#  print "</div></div>"
  l1.modify_base(gtk.STATE_NORMAL,c1)
  l1.modify_text(gtk.STATE_NORMAL,c2)
  l2.modify_base(gtk.STATE_NORMAL,c2)
  l2.modify_text(gtk.STATE_NORMAL,c1)
  pair.pack_start(l1,0,0,0)
  pair.pack_start(l2,0,0,0)
  box.pack_start(pair,0,0,4)

def selColor(caller,source,target,title = "Choose a color"):
  a = gtk.gdk.color_parse(source.get_text())
  d = gtk.ColorSelectionDialog(title)
  c = d.colorsel
  c.set_current_color(a)
  rsp = d.run()
  if rsp == gtk.RESPONSE_OK:
    a = c.get_current_color().to_string()
    b = "#%s%s%s%s%s%s" % (a[1],a[2],a[5],a[6],a[9],a[10])
    b = b.upper()
    source.set_text(b)
    setBack(None,target,source)
  d.destroy()
  return

def setBack(caller,target,field):
  color = field.get_text()
  # print "%s called setBack with %s" % (caller,color)
  try:
    target.modify_base(gtk.STATE_NORMAL,gtk.gdk.color_parse(color)) # change background
  except:
    pass # fail silently

def setFromCombo(caller,program,vals):
  i = 0
  try:
    i = caller.get_active()
  except:
    say(0,"setFromCombo could not read value of %s!\n" % caller)
    return
  if len(vals) >= i:
    program(vals[i])
  else:
    say(0,"Invalid choice passed to setFromCombo: %d > %d!\n" % (i,len(vals)))

def showAbout(caller,parent):
  a = gtk.AboutDialog()
  a.set_program_name("DAOS (Don't Analyze Only--Suggest!)")
  a.set_version(version)
  a.set_website("http://www.github.com/over2sd/daos")
  a.set_authors(["Lincoln Sayger",])
  a.set_comments("Color suggestion GTK frontend.\nReleased June 4, 2012\nThe first version of this utility was a CGI program released July 4, 2008\n Purpose: Give freedom to Web designers by giving them suggestions when their color pairings don't work in an analyzer.") # Tell the user a little bit about this program. Lofty, isn't it?
  a.set_license("  This program is Public Domain. In places where there is no PD,\
  this program is released under a Creatiuve Commons 0 license. In places where\
  that is not honored, this program is released under the following license terms:\
  \n Permission is granted to all persons to use, modify, redistribute, display,\
  and in all other ways derive benefit from this program with or without\
  recognition of its original author, without cost, worldwide, in perpetuity.")
  a.set_wrap_license(True)
  a.set_transient_for(parent)
  a.run()
  a.destroy()

def triggerProcess(caller,c,minr,ming,minb,maxr,maxg,maxb,inc,sizeType,method,hue,target):
  caller.set_sensitive(False)
  c = c.get_text()
  minr = int(minr.get_value()); ming = int(ming.get_value()); minb = int(minb.get_value())
  maxr = int(maxr.get_value()); maxg = int(maxg.get_value()); maxb = int(maxb.get_value())
  inc = int(inc.get_value()); sizeType = sizeType.get_text(); method = method.get_active() + 1
  hue = hue.get_active()
  for x in target.get_children():
    x.destroy()
  print "%s %s-%s %s-%s %s-%s /%s %s: %s? %s" % (c,minr,maxr,ming,maxg,minb,maxb,inc,sizeType,method,hue)
  compileColors(c,minr,ming,minb,maxr,maxg,maxb,inc,sizeType,method=method,hue=hue)
  print colors[0]
  say(1,"Color {0} has {1} good matches in the range of".format(
      c,len(colors))) # Tell the user how many matches were found.
  case = {}
  case['1'] = "all"
  case['17'] = "Web smart"
  case['51'] = "WebSafe"
  say(0,"{0} colors.".format(case[str(inc)]))
  displayColors(method,c,sizeType,target)
  caller.set_sensitive(True)

class Base:
  def __init__(self):
    global status
    global statuswindow
    self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    self.window.set_title("DAOS color suggestion GTK program (Build %s)" % BUILD)
    self.window.connect("delete_event", self.delete_event)
    self.window.connect("destroy", self.destroy)
    self.window.set_border_width(3)
    self.window.show()
    self.window.set_geometry_hints(None,600,400)
    self.window.set_position(gtk.WIN_POS_CENTER_ALWAYS)
    self.box1 = gtk.VBox()
    self.window.add(self.box1)
    self.box1.show()
    qbutton = gtk.Button("Quit")
    qbutton.connect("clicked",self.destroy)
    qbutton.show()
    self.bb = gtk.HBox()
    self.bb.show()
    self.bb.pack_end(qbutton,0,0,2)
    abutton = gtk.Button("About")
    abutton.connect("clicked",showAbout,self.window)
    abutton.show()
    self.bb.pack_end(abutton,0,0,2)
    sbox = statuswindow
    sbox.set_editable(False)
    sbox.set_wrap_mode(gtk.WRAP_WORD)
    sbox.show()
    sbox.set_border_width(2)
    sbox.set_left_margin(7)
    sbox.set_right_margin(7)
    sbox.set_size_request(-1,75)
    sw = gtk.ScrolledWindow()
    sw.set_policy(gtk.POLICY_NEVER,gtk.POLICY_AUTOMATIC)
    sw.show()
    sw.add(sbox)
    self.box1.pack_end(sw,0,1,4)
    self.box1.pack_end(self.bb,0,0,2)

  def main(self):
    say(0,"DAOS color suggestion GTK program v%s (Build %s) loading...\n" % (version,BUILD))
    say(1,"Building interface...")
    buildUI(self.box1,self.bb)
    say(0,"Ready.\n")
    gtk.main()

  def delete_event(self,widget,event,data=None):
    print self.window.get_size()
#    print "delete event occurred"
    return False

  def destroy(self,widget,data=None):
    gtk.main_quit()

if __name__ == "__main__":
  print "...",
  OUTPUT = "gtk"
  base = Base()
  base.main()
