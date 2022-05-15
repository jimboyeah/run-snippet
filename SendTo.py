import os
import re
import sys
import sublime_api as sapi
import sublime
from sublime import *
from sublime_plugin import *
from datetime import datetime

if( hasattr(sapi, "dymenu") ):
  print("sapi.dymenu: %s" % (sapi.dymenu or "None"))
sapi.dymenu = "BADAPPLE"

class SendToCommand(WindowCommand):
  """ SendToCommand
  Send file to other Sublime Text windows

  REF:
  https://wbond.net/sublime_packages/sftp
  https://github.com/absop/ST-dctxmenu/blob/main/menu.py

    1. sublime.dymenu = "Temporaty data used for plugin after reloaded"
    2. modify Context.sublime-menu
    3. sublime_plugin.reload_plugin(__name__)
  """
  # def __init__(self, window):
  #   super(SendToCommand, self).__init__()
  #   self.window = window

  def is_enabled(self):
    return None is not self.window.active_view().file_name()

  def run(self, id=-1, file=None):
    # return reload_plugin("RunSnippet.SendTo")

    items = []
    for it in sublime.windows():
      name = str(it.project_file_name())
      name = re.split(r"[/\\]", name)[-1]
      items.append(str(len(items)) + " - " + name)

    print(id, len(items), file)
    if id < len(items) and id>=0 and os.path.isfile(file):
      self.on_select(id, file)
    else:
      sublime.active_window().active_view().show_popup_menu(items, self.on_select)
      pass

  def on_select(self, index, file_name = None):
    if file_name is None:
      file_name = sublime.active_window().active_view().file_name()
    print({"On select message": items[index], "file_name": file_name})
    sublime.windows()[index].open_file(file_name)
    sublime.windows()[index].bring_to_front()

