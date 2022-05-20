import sys
import sublime_api as sapi
from sublime import *
from sublime_plugin import *

'''
- User/RunSnippet.sublime-settings
- RunSnippet/material/bash 5.1.md
- RunSnippet/material/linux_cli_script_bible.md
'''

_Default = {
    "_filename": "RunSnippet.sublime-settings",
    "jump_between_group": True,
}

# RSettings = None

# __all__ = ["RSettings"]

def init(target, default):
    for key in default:
        if target.has(key) or key.startswith("_"):
            continue
        target.set(key, default[key])

def load():
    global RSettings, _Default
    RSettings = load_settings(_Default['_filename'])
    return RSettings

def save():
    global RSettings, _Default
    save_settings(_Default['_filename'])

def get(key):
    global RSettings
    if not RSettings:
        load()
        print("RSettings reload:", RSettings)
    return RSettings.get(key)

def on_change():
    global RSettings, _Default
    load()
    print("settings on_change")
    print("Load", _Default['_filename'], RSettings)
    if RSettings:
        print("  ==> jump_between_group", RSettings.get("jump_between_group"))

# Load settings from /Packages/Users
# RSettings = load_settings(_Default['_filename'])
load()
RSettings.add_on_change('setting', on_change)
init(RSettings, _Default)
# Save settings to /Packages/Users
# RSettings = save_settings(_Default['_filename'])
save()


# class RSettings(Settings):
#     """docstring for Setting"""
#     def __init__(self, arg):
#         super(Setting, self).__init__()
#         self.arg = arg
