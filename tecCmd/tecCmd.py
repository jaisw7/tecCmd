#!/usr/bin/env python

import sys
import os
import io
import subprocess
import numpy as np
from numpy import *
from tecplot.constant import *
import tecplot as tp
from scipy.special import *
#import commands
import warnings

HISTFILE = os.environ['HOME']+'/.tecCmd_history'
DEFAULT_MLP_IMG = '/tmp/temp_'+str(os.getpid())+'.png'
BANNER = """
        T E C C M D 
        Version 0.0.1    last modified 2018-04-05
        Wrapper for pytecplot. Mimics gnuplot script format!

        Copyright (C) 2018
        Shashank Jaiswal, jaisw7@gmail.com

        tecplot home:     http://www.tecplot.com
        immediate help:   type "help" 
"""


def setupEnv():
  print( BANNER)
  if not os.path.exists(HISTFILE):
    f = open(HISTFILE, 'w+');
    f.close();
  #return load_abort_and_exit_bindings()

########################

class tecInterpreter:
  def __init__(self):
    # get handle to the active frame and set plot type to XY Line
    #self.page = tp.active_page()
    #self.frame = self.page.add_frame()
    self.frame = tp.active_frame()
    # get handle to the active frame and set plot type to XY Line
    if(not self.frame.has_dataset):
        self.frame.create_dataset('Data', ['x', 'y'])
    dummy_zone = self.frame.dataset.add_ordered_zone("-1", 3)
    dummy_zone.values('x')[:] = [1,2,3]
    dummy_zone.values('y')[:] = [1,2,3]
    self.frame.plot_type = PlotType.XYLine
    self.frame.show_border = False
    # set plot type
    self.myPlot = self.frame.plot()
    self.myPlot.activate()
    self.myPlot.show_symbols = True
    self.myPlot.linemap(0).show = False
    #plot.show_lines = True
  
    # Set the x-axis label
    self.myPlot.axes.x_axis(0).title.title_mode = AxisTitleMode.UseText
    self.myPlot.axes.x_axis(0).title.text = ''

    # Set the y-axis label
    self.myPlot.axes.y_axis(0).title.title_mode = AxisTitleMode.UseText
    self.myPlot.axes.y_axis(0).title.text = ''

    # Turn on legend
    self.myPlot.legend.show = True
    self.myPlot.legend.box.box_type = TextBox.None_
    self.myPlot.legend.position = (90, 90)
    
    # storage variables
    self.lineSymbols = []
    self.lineColors = []
    self.outFile = DEFAULT_MLP_IMG
    self.setRange=False
    self.xRange=(1,3)
    self.yRange=(1,3)
    self.delimiter=' '
    self.labels=[]

  def evalStr(self, arg):
    if(not isinstance(arg,str)):
        arg = str(arg)  
    if((arg[0]=="'" and arg[-1]=="'") or (arg[0]=='"' and arg[-1]=='"')):
        arg = arg[1:-1]; 
    return arg;

  def fixStr(self, arg):
    assert isinstance(arg, list), "Needs list input"
    argNew=[]
    count = 0
    while(count!=len(arg)):
      anArg=arg[count]
      if(
        (anArg.startswith("'") and (not anArg.endswith("'"))) or
        (anArg.startswith('"') and (not anArg.endswith('"')))
      ):
        fullCommand=anArg
        while(True):
          count = count + 1
          anArg=arg[count]
          fullCommand=fullCommand + ' ' + anArg 
          if(
            (anArg.endswith("'") and (not anArg.startswith("'"))) or
            (anArg.endswith('"') and (not anArg.startswith('"')))
          ):
            count=count+1
            break
        argNew.append(fullCommand)
      else:
        argNew.append(anArg)
        count=count+1
    return argNew

  def split(self, arg, dl):
    argNew=[]
    nSQ = 0
    nDQ = 0
    start=0
    count=0
    for aChar in arg:
      if(aChar=="'"):
        if(nSQ == 0):
          nSQ = nSQ + 1
        elif(nSQ == 1):
          nSQ = nSQ - 1
      if(aChar=='"'):
        if(nDQ == 0):
          nDQ = nDQ + 1
        elif(nDQ == 1):
          nDQ = nDQ - 1
      if(aChar==dl and nSQ==0 and nDQ==0):
        argNew.append(arg[start:count])
        start = count+1
      count = count + 1
    if(not start==count):
       argNew.append(arg[start:count]) 
    #print( "::", argNew)
    argNew=list(filter(None, argNew))
    return argNew
 

  def filterComment(self, user_input):
    try:
      idx = user_input.index("#")
      user_input = user_input[0:idx]
    except:
      pass
    return user_input

  def runScript(self, scriptFile):
    lines = [line.rstrip('\n') for line in open(scriptFile)]
    linesNew = []
    fullCommand=''
    for line in lines:
      if(line.endswith("\\")):
        fullCommand = fullCommand + line[:-1]
        continue
      if(not fullCommand==''):
        fullCommand = fullCommand + line
      else:
        fullCommand = line
      linesNew.append(fullCommand)
      fullCommand=''
    lines=linesNew
    for user_input in lines:
      user_input = self.filterComment(user_input)
      if(user_input):
        print( user_input)
        cmd = user_input.strip().split(" ");
        #cmd = self.fixStr(cmd)
        if hasattr(self, cmd[0]):
          cmdClass = getattr(self, cmd[0]) #globals()[cmd[0]]
          instance = cmdClass(self, " ".join(cmd[1:]))
        else:
          print( 'unknown command', cmd[0])

  class exit():
    def __init__(self, parent, command):
      sys.exit()

  class unset():
    def __init__(self, parent, command):
      self.parent = parent
      cmd = command.strip().split(" ");
      if hasattr(self, cmd[0]):
        cmdClass = getattr(self, cmd[0]) #globals()[cmd[0]]
        instance = cmdClass(self, " ".join(cmd[1:]))
      else:
        print( 'unknown command', cmd[0])

    class label():
      def __init__(self, parent, command):
        self.parent = parent
        try:
            labelNo = int(command.strip())
            assert labelNo<=len(self.parent.parent.labels), "Invalid label index"
            self.parent.parent.frame.delete_text(
              self.parent.parent.labels[labelNo-1]
            )
            del self.parent.parent.labels[labelNo-1]
        except:
            print( 'issue with the label ', command )

    class logscale():
      def __init__(self, parent, command):
        if(command=='x'):
          parent.parent.myPlot.axes.x_axis(0).log_scale = False
        elif(command=='y'):
          parent.parent.myPlot.axes.y_axis(0).log_scale = False
        else:
          print( "Unknown axis", command)
 

  class keyword():
    def __init__(self, parent, command):
      d = dict(locals(), **globals())
      exec(parent.evalStr(command), locals(), globals())

  class halt():
    def __init__(self, parent, command):
      sys.exit()

  class echo():
    def __init__(self, parent, command):
      d = dict(locals(), **globals())
      exec('print( '+parent.evalStr(command)+')', locals(), globals())

  class set():
    def __init__(self, parent, command):
      self.parent = parent
      cmd = command.strip().split(" ");
      if hasattr(self, cmd[0]):
        cmdClass = getattr(self, cmd[0]) #globals()[cmd[0]]
        instance = cmdClass(self, " ".join(cmd[1:]))
      else:
        print( 'unknown command', cmd[0])

    class ylabel(object):
      def __init__(self, parent, command, axno=0):
        self.parent = parent
        self.ax=parent.parent.myPlot.axes.y_axis(axno)
        cmd = command.strip().split(" ");
        if hasattr(self, cmd[0]):
          cmdClass = getattr(self, cmd[0]) #globals()[cmd[0]]
          instance = cmdClass(self, " ".join(cmd[1:]))
        else:
          try:
            self.ax.title.text = (
                parent.parent.evalStr(" ".join(cmd[0:]))
            )
          except:
            print( 'unknown command', cmd[0])

      def text(self, parent, command):
        try:
          title = parent.parent.parent.evalStr(command.strip())
          self.ax.title.text = title
        except:
            print( "spacing should be a float")

      def color(self, parent, command):
        try:
          arg = parent.parent.parent.evalStr(command.strip())
          try:
            selectedEnum = eval('Color.'+arg)
          except:
            selectedEnum = eval('Color.'+arg.capitalize())
          self.ax.title.color = selectedEnum
        except:
          print( "color should be a string")

      def offset(self, parent, command):
        try:
          arg = float(command.strip())
          self.ax.title.offset = arg
        except:
          print( "offset should be a float")

      def font(self, parent, command):
        try:
          argNew=parent.parent.parent.evalStr(command.strip())
          idx = argNew.index(',')
          fontFace = str(argNew[0:idx])
          fontSize = int(argNew[idx+1:])
          self.ax.title.font.size = fontSize
          self.ax.title.font.typeface = fontFace
        except:
          print( "Error in font", command)


    class y2label(ylabel):
      def __init__(self, parent, command, axno=1):
        self.parent = parent
        self.ax=parent.parent.myPlot.axes.y_axis(axno)
        self.ax.title.title_mode = AxisTitleMode.UseText
        cmd = command.strip().split(" ");
        if hasattr(self, cmd[0]):
          cmdClass = getattr(self, cmd[0]) #globals()[cmd[0]]
          instance = cmdClass(self, " ".join(cmd[1:]))
        else:
          try:
            self.ax.title.text = (
              parent.parent.evalStr(" ".join(cmd[0:]))
            )
          except:
            print( 'unknown command', cmd[0])


    class xlabel(ylabel):
      def __init__(self, parent, command, axno=0):
        self.parent = parent
        self.ax=parent.parent.myPlot.axes.x_axis(axno)
        cmd = command.strip().split(" ");
        if hasattr(self, cmd[0]):
          cmdClass = getattr(self, cmd[0]) #globals()[cmd[0]]
          instance = cmdClass(self, " ".join(cmd[1:]))
        else:
          try:
            self.ax.title.text = (
                parent.parent.evalStr(" ".join(cmd[0:]))
            )
          except:
            print( 'unknown command', cmd[0])


    class x2label(ylabel):
      def __init__(self, parent, command, axno=1):
        self.parent = parent
        self.ax=parent.parent.myPlot.axes.x_axis(axno)
        self.ax.title.title_mode = AxisTitleMode.UseText
        cmd = command.strip().split(" ");
        if hasattr(self, cmd[0]):
          cmdClass = getattr(self, cmd[0]) #globals()[cmd[0]]
          instance = cmdClass(self, " ".join(cmd[1:]))
        else:
          try:
            self.ax.title.text = (
                parent.parent.evalStr(" ".join(cmd[0:]))
            )
          except:
            print( 'unknown command', cmd[0])


    class logscale():
      def __init__(self, parent, command):
        if(command=='x'):
          parent.parent.myPlot.axes.x_axis(0).log_scale = True
        elif(command=='y'):
          parent.parent.myPlot.axes.y_axis(0).log_scale = True
        else:
          print( "Unknown axis", command)
        

    class xrange():
      def __init__(self, parent, command):
        try:
          idx = command.strip().index(":")
          minLim = float(command[1:idx])
          maxLim = float(command[idx+1:-1])
          parent.parent.myPlot.axes.x_axis(0).min = minLim
          parent.parent.myPlot.axes.x_axis(0).max = maxLim
          parent.parent.setRange=True
          parent.parent.xRange=(minLim,maxLim)
        except:
          print( "xrange need to be in format [min:max]")


    class ygridlines():
      def __init__(self, parent, command, axno=0):
        self.parent = parent
        self.ax=parent.parent.myPlot.axes.y_axis(axno)
        setCmd = str(command).strip().split(" ");
        if(not setCmd):
          print( "key command empty", command)
        for i in range(0,len(setCmd),2):
          subCmd = setCmd[i]
          subCmdArg = setCmd[i+1]
          if hasattr(self, subCmd):
            subCmdFun = getattr(self, subCmd)
            result = subCmdFun(parent, subCmdArg)
          else:
            print( 'unknown command', subCmd)
     
      def on(self, parent, command):
        try:
          idx = str(command.strip())
          self.ax.grid_lines.show = True
        except:
            print( "spacing should be a float")

      def off(self, parent, command):
        try:
          idx = str(command.strip())
          self.ax.grid_lines.show = False
        except:
            print( "spacing should be a float")

      def dt(self, parent, command):
        try:
          arg = self.parent.parent.evalStr(command.strip())
          try:
            selectedEnum = eval('LinePattern.'+arg)
          except:
            selectedEnum = eval('LinePattern.'+arg.capitalize())
          self.ax.grid_lines.line_pattern = selectedEnum
        except:
          print( "dash type should be a string")

      def color(self, parent, command):
        try:
          arg = self.parent.parent.evalStr(command.strip())
          try:
            selectedEnum = eval('Color.'+arg)
          except:
            selectedEnum = eval('Color.'+arg.capitalize())
          self.ax.grid_lines.color = selectedEnum
        except:
          print( "color should be a string")

      def lt(self, parent, command):
        try:
          arg = float(str(command.strip()))
          self.ax.grid_lines.line_thickness = arg
        except:
          print( "line thickness should be a float")

      def pl(self, parent, command):
        try:
          arg = float(str(command.strip()))
          self.ax.grid_lines.pattern_length = arg
        except:
          print( "pattern length should be a float")


    class y2gridlines(ygridlines):
      def __init__(self, parent, command, axno=1):
        self.parent = parent
        self.ax=parent.parent.myPlot.axes.y_axis(axno)
        setCmd = str(command).strip().split(" ");
        if(not setCmd):
          print( "key command empty", command)
        for i in range(0,len(setCmd),2):
          subCmd = setCmd[i]
          subCmdArg = setCmd[i+1]
          if hasattr(self, subCmd):
            subCmdFun = getattr(self, subCmd)
            result = subCmdFun(parent, subCmdArg)
          else:
            print( 'unknown command', subCmd)


    class xgridlines(ygridlines):
      def __init__(self, parent, command, axno=0):
        self.parent = parent
        self.ax=parent.parent.myPlot.axes.x_axis(axno)
        setCmd = str(command).strip().split(" ");
        if(not setCmd):
          print( "key command empty", command)
        for i in range(0,len(setCmd),2):
          subCmd = setCmd[i]
          subCmdArg = setCmd[i+1]
          if hasattr(self, subCmd):
            subCmdFun = getattr(self, subCmd)
            result = subCmdFun(parent, subCmdArg)
          else:
            print( 'unknown command', subCmd)


    class x2gridlines(ygridlines):
      def __init__(self, parent, command, axno=1):
        self.parent = parent
        self.ax=parent.parent.myPlot.axes.x_axis(axno)
        setCmd = str(command).strip().split(" ");
        if(not setCmd):
          print( "key command empty", command)
        for i in range(0,len(setCmd),2):
          subCmd = setCmd[i]
          subCmdArg = setCmd[i+1]
          if hasattr(self, subCmd):
            subCmdFun = getattr(self, subCmd)
            result = subCmdFun(parent, subCmdArg)
          else:
            print( 'unknown command', subCmd)


    class yticks():
      def __init__(self, parent, command, axno=0):
        self.parent = parent
        self.ax=parent.parent.myPlot.axes.y_axis(axno)
        #cmd = command.strip().split(" ");
        #if hasattr(self, cmd[0]):
        #  cmdClass = getattr(self, cmd[0]) #globals()[cmd[0]]
        #  instance = cmdClass(parent, " ".join(cmd[1:]))
        #else:
        #  print( 'unknown command', cmd[0])
        setCmd = command.strip().split(" ");
        if(not setCmd):
          print( "yticks command empty", command)
        for i in range(0,len(setCmd),2):
          subCmd = setCmd[i]
          subCmdArg = setCmd[i+1]
          if hasattr(self, subCmd):
            subCmdFun = getattr(self, subCmd)
            result = subCmdFun(parent, subCmdArg)
          else:
            print( 'unknown command', subCmd)

      def spacing(self, parent, command):
        #warnings.warn("should come after the plot command", UserWarning)
        try:
          idx = float(str(command.strip()))
          self.ax.ticks.auto_spacing = False
          self.ax.ticks.spacing = idx
        except:
          if(command=='auto'):
            self.ax.ticks.auto_spacing = True
          else:
            print( "spacing should be a float")

      def format(self, parent, command):
        try:
          arg = parent.parent.evalStr(command.strip())
          selectedEnum = eval('NumberFormat.'+arg)
          self.ax.tick_labels.format.format_type = selectedEnum
        except:
          print( "format should be a string")

      def color(self, parent, command):
        try:
          arg = parent.parent.evalStr(command.strip())
          try:
            selectedEnum = eval('Color.'+arg)
          except:
            selectedEnum = eval('Color.'+arg.capitalize())
          self.ax.tick_labels.color = selectedEnum
          self.ax.line.color = selectedEnum
        except:
          print( "color should be a string")

      def angle(self, parent, command):
        try:
          arg = float(str(command.strip()))
          self.ax.tick_labels.angle = arg
        except:
          print( "angle should be a float")

      def precision(self, parent, command):
        try:
          arg = int(str(command.strip()))
          self.ax.tick_labels.format.precision = arg
        except:
          print( "precision should be a int")


    class y2ticks(yticks):
      def __init__(self, parent, command, axno=1):
        self.parent = parent
        self.ax=parent.parent.myPlot.axes.y_axis(axno)
        #cmd = command.strip().split(" ");
        #if hasattr(self, cmd[0]):
        #  cmdClass = getattr(self, cmd[0]) #globals()[cmd[0]]
        #  instance = cmdClass(parent, " ".join(cmd[1:]))
        #else:
        #  print( 'unknown command', cmd[0])
        setCmd = command.strip().split(" ");
        if(not setCmd):
          print( "y2ticks command empty", command)
        for i in range(0,len(setCmd),2):
          subCmd = setCmd[i]
          subCmdArg = setCmd[i+1]
          if hasattr(self, subCmd):
            subCmdFun = getattr(self, subCmd)
            result = subCmdFun(parent, subCmdArg)
          else:
            print( 'unknown command', subCmd)

    class xticks(yticks):
      def __init__(self, parent, command, axno=0):
        self.parent = parent
        self.ax=parent.parent.myPlot.axes.x_axis(axno)
        #cmd = command.strip().split(" ");
        #if hasattr(self, cmd[0]):
        #  cmdClass = getattr(self, cmd[0]) #globals()[cmd[0]]
        #  instance = cmdClass(parent, " ".join(cmd[1:]))
        #else:
        #  print( 'unknown command', cmd[0])
        setCmd = command.strip().split(" ");
        if(not setCmd):
          print( "xticks command empty", command)
        for i in range(0,len(setCmd),2):
          subCmd = setCmd[i]
          subCmdArg = setCmd[i+1]
          if hasattr(self, subCmd):
            subCmdFun = getattr(self, subCmd)
            result = subCmdFun(parent, subCmdArg)
          else:
            print( 'unknown command', subCmd)

    class x2ticks(yticks):
      def __init__(self, parent, command, axno=1):
        self.parent = parent
        self.ax=parent.parent.myPlot.axes.x_axis(axno)
        #cmd = command.strip().split(" ");
        #if hasattr(self, cmd[0]):
        #  cmdClass = getattr(self, cmd[0]) #globals()[cmd[0]]
        #  instance = cmdClass(parent, " ".join(cmd[1:]))
        #else:
        #  print( 'unknown command', cmd[0])
        setCmd = str(command).strip().split(" ");
        if(not setCmd):
          print( "x2ticks command empty", command)
        for i in range(0,len(setCmd),2):
          subCmd = setCmd[i]
          subCmdArg = setCmd[i+1]
          if hasattr(self, subCmd):
            subCmdFun = getattr(self, subCmd)
            result = subCmdFun(parent, subCmdArg)
          else:
            print( 'unknown command', subCmd)

    class yrange():
      def __init__(self, parent, command, axno=0):
        self.ax = parent.parent.myPlot.axes.y_axis(axno)
        try:
          idx = command.strip().index(":")
          minLim = float(command[1:idx])
          maxLim = float(command[idx+1:-1])
          self.ax.min = minLim
          self.ax.max = maxLim
          #self.ax.fit_range()
          parent.parent.setRange=True
          #parent.parent.yRange=(minLim,maxLim)
        except:
          print( "yrange need to be in format [min:max]")

    class y2range():
      def __init__(self, parent, command, axno=1):
        warnings.warn("should come after the plot command")
        self.ax = parent.parent.myPlot.axes.y_axis(axno)
        try:
          idx = command.strip().index(":")
          minLim = float(command[1:idx])
          maxLim = float(command[idx+1:-1])
          self.ax.min = minLim
          self.ax.max = maxLim
          #self.ax.fit_range()
          parent.parent.setRange=True
          #parent.parent.yRange=(minLim,maxLim)
        except:
          print( "y2range need to be in format [min:max]")


    class legend():
      def __init__(self, parent, command):
        self.parent = parent
        cmd = command.strip().split(" ");
        if hasattr(self, cmd[0]):
          cmdClass = getattr(self, cmd[0]) #globals()[cmd[0]]
          instance = cmdClass(self, " ".join(cmd[1:]))
        else:
          print( 'unknown command', cmd[0])

      class row_spacing():
        def __init__(self, parent, command):
          try:
            idx = float(str(command.strip()))
            parent.parent.parent.myPlot.legend.row_spacing = idx
          except:
            print( "row_spacing should be a float")

      class font():
        def __init__(self, parent, command):
          try:
            argNew=parent.parent.parent.evalStr(command.strip())
            idx = argNew.index(',')
            fontFace = str(argNew[0:idx])
            fontSize = float(argNew[idx+1:])
            parent.parent.parent.myPlot.legend.font.size = fontSize
            parent.parent.parent.myPlot.legend.font.typeface = fontFace
          except:
            print( "Error in font", command)


    class out():
      def __init__(self, parent, command):
        if(not command.strip()==''):
          parent.parent.outFile = parent.parent.evalStr(command)
        else:
          # save image to file
          #tp.export.save_png(parent.parent.outFile, 600, supersample=3)
          tp.export.save_ps(parent.parent.outFile)
          tp.save_layout(parent.parent.outFile+'.lpk', include_data=True)
          parent.parent.myPlot.delete_linemaps()
          #parent.parent.page.delete_frame(parent.parent.frame)
          #parent.parent.__init__(parent.parent.__manager__)

    class key():
      def __init__(self, parent, command):
        self.parent = parent
        setCmd = str(command).strip().split(" ");
        if(not setCmd):
          print( "key command empty", command)
        for i in range(0,len(setCmd),2):
          subCmd = setCmd[i]
          subCmdArg = setCmd[i+1]
          if hasattr(self, subCmd):
            subCmdFun = getattr(self, subCmd)
            result = subCmdFun(subCmdArg)
          else:
            print( 'unknown command', subCmd)

      def at(self, arg):
        try:
          idx = arg.index(',')
          legendX = int(arg[0:idx])
          legendY = int(arg[idx+1:])
          #print( legendX, legendY)
          self.parent.parent.myPlot.legend.position=(legendX, legendY)
        except:
          print( "Error in key position", arg)

      def show(self, arg):
        try:
          val=bool(arg)
          self.parent.parent.myPlot.legend.show=False
        except:
          print( "Error in key show", arg)


      def samplen(self,arg):
        try:
          samplen=int(arg)
        except:
          print( "Error in key samplen", arg)

      def font(self, arg):
        try:
          argNew=parent.parent.parent.evalStr(command.strip())
          idx = argNew.index(',')
          fontFace = str(argNew[0:idx])
          fontSize = float(argNew[idx+1:])
          self.parent.parent.myPlot.legend.font.size = fontSize
          self.parent.parent.myPlot.legend.font.typeface = fontFace
        except:
          print( "Error in font", command)


    class line():
      def __init__(self, parent, command):
        self.parent = parent
        self.lineX=0
        self.lineY=0
        self.dispX=0.1
        self.dispY=0.1
        self.linePattern = 'SOLID'
        setCmd = str(command).strip().split(" ");
        setCmd=self.parent.parent.fixStr(setCmd)
        if(not setCmd):
          print( "line command empty", command)
        for i in range(0,len(setCmd),2):
          subCmd = setCmd[i]
          subCmdArg = setCmd[i+1]
          if hasattr(self, subCmd):
            subCmdFun = getattr(self, subCmd)
            result = subCmdFun(subCmdArg)
          else:
            print( 'unknown command', subCmd)
        self.__addLine__()

      def __executeMacro__(self,macroStr, tempFile = '_temp.mcr', unlink=True):
        # Note: macro execution is asynchronous process
        f = open(tempFile, 'w')
        f.write(macroStr)
        f.close()
        tp.macro.execute_file(tempFile)
        if unlink: os.unlink(tempFile)

      def __addLine__(self):
        self.__executeMacro__(r'''#!MC 1410
          $!ATTACHGEOM
          GEOMTYPE = LINESEGS
          ANCHORPOS
            {
            X = '''+str(self.lineX)+'''
            Y = '''+str(self.lineY)+'''
            }
          ISFILLED = YES
          FILLCOLOR = CUSTOM2
          LINEPATTERN = '''+str(self.linePattern)+'''
          LINETHICKNESS = 0.4
          RAWDATA
          1
          2
          0 0
          '''+str(self.dispX)+''' '''+str(self.dispY)+'''
        ''')
 
      def dt(self, arg):
        try:
          arg=self.parent.parent.evalStr(arg)
          arg =arg.upper()
          self.linePattern = arg
        except:
          print( "Error in dt", arg)

      def at(self, arg):
        try:
          idx = arg.index(',')
          self.lineX = float(arg[0:idx])
          self.lineY = float(arg[idx+1:])
        except:
          print( "Error in line position", arg)
     
      def disp(self, arg):
        try:
          idx = arg.index(',')
          self.dispX = float(arg[0:idx])
          self.dispY = float(arg[idx+1:])
        except:
          print( "Error in disp position", arg)


    class label():
      def __init__(self, parent, command):
        self.parent = parent
        self.labelX=0
        self.labelY=0
        self.fontFace="Helvetica"
        self.fontSize=14
        self.color=Color.Black
        setCmd = str(command).strip().split(" ");
        setCmd=self.parent.parent.fixStr(setCmd)
        self.text = self.parent.parent.evalStr(setCmd[0])
        if(not setCmd):
          print( "label command empty", command)
        for i in range(1,len(setCmd),2):
          subCmd = setCmd[i]
          subCmdArg = setCmd[i+1]
          if hasattr(self, subCmd):
            subCmdFun = getattr(self, subCmd)
            result = subCmdFun(subCmdArg)
          else:
            print( 'unknown command', subCmd)
        self.parent.parent.labels.append(
          self.parent.parent.frame.add_text(
            self.text, position=(self.labelX, self.labelY), 
            coord_sys=CoordSys.Grid, 
            typeface=self.fontFace, bold=True, italic=False, 
            size_units=Units.Point, size=self.fontSize, color=self.color, angle=None, 
            line_spacing=None, anchor=None, box_type=None, 
            line_thickness=None, box_color=None, 
            fill_color=None, margin=None, zone=None
          )
        )
 
      def font(self, arg):
        try:
          argNew=self.parent.parent.evalStr(arg)
          idx = argNew.index(',')
          self.fontFace = str(argNew[0:idx])
          self.fontSize = int(argNew[idx+1:])
        except:
          print( "Error in font", arg)

      def tc(self, arg):
        try:
          arg=self.parent.parent.evalStr(arg)
          arg =arg.capitalize()
          if(len(arg)>=2):
            try:
              selectedEnum = eval('Color.'+arg)
              self.color = selectedEnum
            except:
              print( "unknown color:", arg)
          else:
            try:
              argNum = int(arg);
              self.color = Color(argNum)
            except:
              print( "unknown color:", arg)
        except:
          print( "Error in color", arg)

      def at(self, arg):
        try:
          idx = arg.index(',')
          self.labelX = float(arg[0:idx])
          self.labelY = float(arg[idx+1:])
        except:
          print( "Error in label position", arg)

    class datafile():
      def __init__(self, parent, command):
        self.parent = parent
        setCmd = str(command).strip().split(" ");
        if(not setCmd):
          print( "datafile command empty", command)
        for i in range(0,len(setCmd),2):
          subCmd = setCmd[i]
          subCmdArg = setCmd[i+1]
          if hasattr(self, subCmd):
            subCmdFun = getattr(self, subCmd)
            result = subCmdFun(subCmdArg)
          else:
            print( 'unknown command', subCmd)
 
      def separator(self, arg):
        try:
          self.parent.parent.delimiter=self.parent.parent.evalStr(arg)
        except:
          print( "Error in separator", arg)


  class plot():
    def __init__(self, parent, command):
      self.parent = parent;
      self.command = command;
      self.__initDefaults__();
      self.parseArgs();

    def __initDefaults__(self):
      self.frame = self.parent.frame
      self.dashType = LinePattern.Solid
      self.lineSymbol = ''
      self.legendName = ''
      self.yaxesindex = 0
      self.lineOrSymbol = 1
      self.lineColor = ''
      self.lineThickness = 0.5
      self.symbolStep = 1
      self.fileName = ''
      self.xInfo = ''
      self.yInfo = ''
      self.everyStep = 0
      self.fill = 'yes'
      self.symbolThickness = 0.1
      self.numZones=1

    def __finalize__(self):
      matrix = []
      try:
        if(self.parent.delimiter==' '):
          matrix = np.loadtxt(
            self.fileName, dtype=np.float,
            comments='#', skiprows=0
          )
        else:
          matrix = np.loadtxt(
            self.fileName, dtype=np.float,
            comments='#', delimiter=self.parent.delimiter,
            skiprows=0
          )
        matrix = np.c_[matrix]
      except:
        print( "problem with file, skipping", self.fileName)
        return
      x=eval(self.xInfo)
      y=eval(self.yInfo)
      if(any(x) and any(y)):
        if(not self.everyStep==0):
          x = x[0::self.everyStep]
          y = y[0::self.everyStep]
        if(self.lineSymbol==''):
          t = [symbol.value for symbol in self.parent.lineSymbols]
          self.lineSymbol = GeomShape.Circle
          if(t):
            t = sorted(t)
            minimum = t[0]-1
            i = 1
            while i<len(t):
              if(not t[i]==t[i-1]-1):
                minimum = t[i]-1
                break
              i = i+1
            minimum = minimum%7
            self.lineSymbol = GeomShape(minimum)
        if(self.lineColor==''):
          t = [color.value for color in self.parent.lineColors]
          self.lineColor = Color.Red
          if(t):
            t = sorted(t)
            minimum = t[0]+1
            i = 1
            while i<len(t):
              if(not t[i]==t[i-1]+1):
                minimum = t[i]+1
                break
              i = i+1
            minimum = minimum%len(Color)
            self.lineColor = Color(minimum)
        if(self.lineThickness == 0.5 and self.lineOrSymbol==0):
          self.lineThickness = 1.5 
        
        self.parent.lineSymbols.append(self.lineSymbol)
        self.parent.lineColors.append(self.lineColor)

        zoneSize=len(x.ravel())/self.numZones
        assert zoneSize==int(zoneSize), "numZones"+numZones+"should be a divisor of data-size"+str(len(x.ravel()))        
        zoneSize = int(zoneSize)

        zs=0
        for aZone in range(self.numZones):
          uid = str(hash(self.legendName+str(len(self.parent.lineSymbols)-1)+str(aZone)))
          ds = self.frame.dataset
          rect_zone = ds.add_ordered_zone(uid, zoneSize)
          rect_zone.values('x')[:] = x.ravel()[zs:zs+zoneSize]
          rect_zone.values('y')[:] = y.ravel()[zs:zs+zoneSize]
          #tp.session.zones_added(rect_zone)

          # loop over the linemaps, setting style for each
          self.parent.myPlot.activate()
          lmap = self.parent.myPlot.add_linemap(
              uid, rect_zone, ds.variable('x'), ds.variable('y'), True
          )
          lmap.show = True
          lmap.y_axis_index = self.yaxesindex
          lmap.name = self.legendName #This will be used in the legend
          if(self.parent.setRange==False):
             self.parent.myPlot.view.fit_data()
          if(self.legendName=='' or (not zs==0)):
            lmap.show_in_legend=False
          if(self.lineOrSymbol==1):
            lmap.symbols.show = False
            lmap.line.show = True
            line = lmap.line
            line.color = self.lineColor
            line.line_thickness = self.lineThickness
            line.line_pattern = self.dashType
            #line.pattern_length = 0.3*count
          elif(self.lineOrSymbol==0):
            lmap.line.show = False
            symbols = lmap.symbols
            symbols.show = True
            symbols.symbol().shape = self.lineSymbol 
            symbols.color = self.lineColor
            symbols.step = self.symbolStep
            symbols.size = self.lineThickness
            if(self.fill=='yes'):
              symbols.fill_mode = FillMode.UseSpecificColor
            else:
              symbols.fill_mode = FillMode.None_
            symbols.fill_color = self.lineColor
            symbols.line_thickness = self.symbolThickness
          elif(self.lineOrSymbol==2):
            self.parent.myPlot.show_symbols=True
            lmap.line.show = True
            symbols = lmap.symbols
            symbols.show = True
            symbols.symbol().shape = self.lineSymbol 
            symbols.color = self.lineColor
            symbols.step = self.symbolStep
            symbols.size = 1.5
            if(self.fill=='yes'):
              symbols.fill_mode = FillMode.UseSpecificColor
            else:
              symbols.fill_mode = FillMode.None_
            symbols.fill_color = self.lineColor
            symbols.line_thickness = self.lineThickness
            line = lmap.line
            line.color = self.lineColor
            line.line_thickness = self.lineThickness
            line.line_pattern = self.dashType
          elif(self.lineOrSymbol==3):
            self.parent.myPlot.show_bars=True
            lmap.symbols.show = False
            lmap.line.show = False
            lmap.bars.show = True
            bars = lmap.bars
            bars.size = self.symbolThickness
            if(self.fill=='yes'):
              bars.fill_mode = FillMode.UseSpecificColor
            else:
              bars.fill_mode = FillMode.None_
            bars.fill_color = self.lineColor
            bars.line_color = self.lineColor
            bars.line_thickness = self.lineThickness
            #line.pattern_length = 0.3*count
          zs = zs + zoneSize
      else:
        print( "problem with file, skipping ", self.fileName)

    def __clear__(self):
      self.parent.lineSymbols = []
      self.parent.lineColors = []
      #self.parent.myPlot.delete_linemaps()


    def parseArgs(self):
      #plotStrs = self.command.split(",");
      plotStrs = self.parent.split(self.command, ",");
      if(not plotStrs):
        print( "incomplete plot command")
        return
      self.__clear__()
      for i in range(len(plotStrs)):
        self.__initDefaults__()
        #plotCmd = str(plotStrs[i]).strip().split(" ");
        plotCmd = self.parent.split(plotStrs[i], " ");
        if(not plotCmd):
          print( "need a filename")
        fileName = self.parent.evalStr(str(plotCmd[0]).strip())
        if(fileName.startswith("system(")):
          # this is a bash command
          bashCommand = fileName
          #print( bashCommand)
          try:
            idxS = bashCommand.strip().index("(")
            idxE = bashCommand.strip().index(")")
            bashCommand = bashCommand[idxS+1:idxE]
            #print( bashCommand)
            bashCommand = self.parent.evalStr(str(bashCommand).strip())
            #bashCommand = self.parent.split(bashCommand)
            bashCommand = bashCommand.split(" ")
            pipes = []
            for i in range(len(bashCommand)):
              bashCommand[i] = self.parent.evalStr(
                str(bashCommand[i]).strip()
              )   
              if(bashCommand[i]=='|'):
                pipes.append(i)
                pipes.append(len(bashCommand))
            fileData=''         
            try:
              #fileData=subprocess.check_output(bashCommand)
              fileData = commands.getoutput(" ".join(bashCommand))
            except:
                print( "Error executing system command:", bashCommand)
            np.savetxt('/tmp/temp_'+str(os.getpid())+'.txt', 
                [fileData], fmt="%s")
            fileName = '/tmp/temp_'+str(os.getpid())+'.txt'
          except:
            print( "error parsing function command")
        elif(fileName.startswith("function(")):
          # this is a function command
          bashCommand = fileName
          #print( bashCommand)
          try:
            idxS = bashCommand.strip().index("(")
            idxE = bashCommand.strip().rindex(")")
            bashCommand = bashCommand[idxS+1:idxE]
            bashCommand = self.parent.evalStr(str(bashCommand).strip())
            func_template = """def func_%s"""
            exec(func_template % (bashCommand))
            #print(func_template % (bashCommand))
            fileData=''         
            try:
                x=np.linspace(self.parent.xRange[0],self.parent.xRange[1],100)
                y=eval('func_(x)')
            except Exception as e:
                print( "Error executing system command:", bashCommand, "\nError", e)
            np.savetxt('/tmp/temp_'+str(os.getpid())+'.txt', y)
            fileName = '/tmp/temp_'+str(os.getpid())+'.txt'
          except:
            print( "error parsing function command")
        #fileName=eval(fileName)
        if not os.path.exists(fileName):
          print( "file", fileName, "does not exist")
          continue
        self.fileName = fileName
        #print( plotCmd)
        for i in range(1,len(plotCmd),2):
          subCmd = plotCmd[i]
          subCmdArg = plotCmd[i+1]
          if hasattr(self, subCmd):
            subCmdFun = getattr(self, subCmd)
            result = subCmdFun(subCmdArg)
          else:
            print( 'unknown command', subCmd)
        self.__finalize__();
      if(self.parent.outFile==DEFAULT_MLP_IMG):
        self.parent.set.out(self, '')
        subprocess.call(["display", # .call(...) will block, Popen won't
          "-immutable", "-antialias", DEFAULT_MLP_IMG]);
        #self.__clear__()

    def using(self, arg):
      argCopy = arg
      try:
        idx = arg.index(':')
        self.xInfo = arg[:idx]
        self.yInfo = arg[idx+1:]
        for i in range(100,-1,-1):
          self.xInfo = self.xInfo.replace('$'+str(i), 'matrix[:,'+str(i-1)+']')
          self.yInfo = self.yInfo.replace('$'+str(i), 'matrix[:,'+str(i-1)+']')
        try:
          int(eval(self.xInfo))
          self.xInfo = "matrix[:,"+str(int(eval(self.xInfo))-1)+"]"
        except:
          pass
        try:
          int(eval(self.yInfo))
          self.yInfo = "matrix[:,"+str(int(eval(self.yInfo))-1)+"]"
        except:
          pass
        #print( self.yInfo)
        if(self.legendName==''):
          self.legendName = argCopy
      except:
        print( "invalid using:", arg)

    def u(self, arg):
      self.using(arg)

    def w(self, arg):
      if(arg=='p'):
        self.lineOrSymbol = 0
      elif(arg=='l'):
        self.lineOrSymbol = 1
      elif(arg=='lp' or arg=='pl'):
        self.lineOrSymbol = 2
      elif(arg=='b'):
        self.lineOrSymbol = 3
      else:
        print( "unknown symbol or line type:", arg)

    def pointtype(self, arg):
      arg = self.parent.evalStr(arg);  
      arg = arg.capitalize()    
      if(len(arg)>=2):
        try:
          selectedEnum = eval('GeomShape.'+arg)
          self.lineSymbol = selectedEnum
        except:
          print( "unknown point type:", arg)
      else:
        try:
          argNum = int(arg);
          self.lineSymbol = GeomShape(argNum)
        except:
          print( "unknown point type:", arg)

    def pt(self, arg):
      self.pointtype(arg)

    def linecolor(self, arg):
      arg = self.parent.evalStr(arg);  
      arg = arg.capitalize()
      if(len(arg)>=2):
        try:
          selectedEnum = eval('Color.'+arg)
          self.lineColor = selectedEnum
        except:
          print( "unknown linecolor:", arg)
      else:
        try:
          argNum = int(arg);
          self.lineColor = Color(argNum)
        except:
          print( "unknown linecolor:", arg)

    def lc(self, arg):
      self.linecolor(arg)

    def symbolfill(self, arg):
      arg = self.parent.evalStr(arg);
      if(arg=='no' or arg=='yes'):
        self.fill=arg
      else:
        print( "unknown arg, need yes or no", arg)

    def sf(self, arg):
      self.symbolfill(arg)

    def symbolthickness(self, arg):
      try:
        float(arg)
      except:
        print( "symbolthickness needs float input, found:", arg)
      self.symbolThickness = float(arg)

    def st(self, arg):
      self.symbolthickness(arg)


    def every(self, arg):
      try:
        int(arg)
      except:
        print( "every needs integer input, found:", arg)
      #if(self.x):
      #  self.x = self.x[1::arg]
      #  self.y = self.y[1::arg]
      self.everyStep = int(arg)

    def symbolstep(self, arg):
      try:
        int(arg)
      except:
        print( "symbolstep needs integer input, found:", arg)
      self.symbolStep = int(arg)

    def ss(self, arg):
      self.symbolstep(arg)

    # the data will be written in form of n-zones
    def nzones(self, arg):
      try:
        int(arg)
      except:
        print( "nzones needs integer input, found:", arg)
      assert int(arg)>=1, "Need a natural number for nzones"
      self.numZones = int(arg)

    def nz(self, arg):
      self.nzones(arg)

    def dashtype(self, arg):
      arg = self.parent.evalStr(arg);  
      #arg = arg.capitalize()
      if(len(arg)>=2):
        try:
          selectedEnum = eval('LinePattern.'+arg)
          self.dashType = selectedEnum
        except:
          print( "unknown dashtype:", arg)
      else:
        try:
          argNum = int(arg);
          self.dashType = LinePattern(argNum)
        except:
          print( "unknown dashtype:", arg)

    def dt(self, arg):
      self.dashtype(arg)

    def linewidth(self, arg):
      try:
        float(arg)
      except:
        print( "every needs float input, found:", arg)
      self.lineThickness = float(arg)

    def lw(self, arg):
      self.linewidth(arg)

    def title(self, arg):
      self.legendName = self.parent.evalStr(arg)

    def t(self, arg):
      self.title(arg)

    def yaxesidx(self, arg):
      try:
        int(arg)
      except:
        print( "yaxesidx needs integer input, found:", arg)
      self.yaxesindex = int(arg)

    def yidx(self, arg):
      self.yaxesidx(arg)



def __main__():

  manager = setupEnv();
  if(len(sys.argv)>1):
    if(os.path.exists(sys.argv[1])):
      tecEnv.runScript(sys.argv[1])
    else:
      print( "Usage: tecCmd scriptFile")
  else:
      print( "Usage: tecCmd scriptFile")
  