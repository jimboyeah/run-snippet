
import os
from code import InteractiveConsole
import urllib
import sublime
import sublime_plugin


class FirstColumnCommand(sublime_plugin.TextCommand):
  def __init__(self, view):
    self.view = view

  def run(self, edit, paths, files):
    print("FirstColumnCommand...")
    selections = self.view.sel()
    lines = []
    for region in selections:
      lines = lines + self.view.lines(region)

    self.view.sel().clear()
    # self.view.sel().add_all(lines)
    for line in lines:
      c1 = self.view.find(r"\t|\s\s+", line.a)
      if(c1.b>line.b) : c1 = sublime.Region(line.a,line.a)
      self.view.sel().add(c1)


class IndexRowsCommand(sublime_plugin.TextCommand):
  def __init__(self, view):
    self.view = view

  def run(self, edit, paths, files):
    view = self.view

    regionset = view.sel()

    circles = '🅐🅑🅒🅓🅔🅕🅖🅗🅘🅙🅚🅛🅜🅝🅞🅟🅠🅡🅢🅣🅤🅥🅦🅧🅨🅩'
    circles = '🄌➊➋➌➍➎➏➐➑➒➓⓫⓬⓭⓮⓯⓰⓱⓲⓳⓴'
    scope = view.scope_name(regionset[0].a)
    circled = scope.find('markup.raw.block.markdown')>-1 or scope.find('source')>-1

    nums = []
    alllines = []
    index = 0
    for region in regionset:
      lines = view.lines(region)
      alllines+=(lines) # list extend
      digi = len(str(len(alllines)))
      for region in lines:
        index += 1
        if circled:
          nums.append(circles[index % len(circles)]);
        else:
          nums.append(str(index).rjust(digi, "0")) # .zfill(3)

    view.sel().clear()
    # for region in regionset:
      # view.sel().subtract(region)

    index = 0
    view.sel().add_all(alllines)
    for region in view.sel():
      if circled:
        view.insert(edit, region.b, nums[index])
      else:
        view.insert(edit, region.a, str(nums[index])+". ")
      index += 1

  def is_enabled(self, *args, **kwargs):
    regionset = self.view.sel()
    return len(regionset)>0 and len(regionset)>1 or regionset[0].b != regionset[0].a 
