import os
from code import InteractiveConsole
import urllib
import sublime
import sublime_plugin


class FirstColumnCommand(sublime_plugin.TextCommand):
  def __init__(self, view):
    self.view = view
    # print("FCC FirstColumnCommand init [%s] [%s]...\n%s\n"%(self, view, __file__))

  def run(self, edit, paths, files):
    # inf(edit) # Print Edit API Information
    # inf(self.view) # Print View API Information
    # inf(self.view.sel()) # Print RegionSet API Information
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
    # print("IRC init [%s] [%s]...\n%s\n"%(self, view, __file__))

  def run(self, edit, paths, files):
    view = self.view
    # print(["IRC run ", view.sel()])
    # FirstColumnCommand(view).run(edit, [], [])

    regionset = view.sel()

    nums = []
    alllines = []
    for region in regionset:
      index = 0
      lines = view.lines(region)
      alllines+=(lines) # list extend
      digi = len(str(len(alllines)))
      for region in lines:
        index += 1
        nums.append(str(index).rjust(digi, "0")) # .zfill(3)

    # print(alllines)
    view.sel().clear()
    # for region in regionset:
      # view.sel().subtract(region)

    index = 0
    view.sel().add_all(alllines)
    for region in view.sel():
      view.insert(edit, region.a, str(nums[index])+". ")
      index += 1

  # def description(self, *args, **kwargs):
  def is_enabled(self, *args, **kwargs):
    regionset = self.view.sel()
    # print("%s is_enabled(self, *args): %s %s" % (self.__class__.__name__, args, kwargs))
    # print(regionset)
    return len(regionset)>0 and len(regionset)>1 or regionset[0].b != regionset[0].a 
