import sys
import sublime_api as sapi
from sublime import *
from sublime_plugin import *

_Default = {
    "_filename": "RunSnippet.sublime-settings",
    "jump_between_group": True,
}

RSettings = None

__all__ = ["RSettings"]

def init(target, default):
    for key in default:
        if target.has(key) or key.startswith("_"):
            continue
        target.set(key, default[key])

def load():
    global RSettings, _Default
    if not RSettings or not RSettings.settings_id:
        print("RSettings reload:", RSettings)
        RSettings = load_settings(_Default['_filename'])
    return RSettings

def save():
    global RSettings, _Default
    save_settings(_Default['_filename'])

def get(key):
    RSettings = load()
    return (RSettings.get(key), RSettings)

def on_change():
    RSettings = load()
    print("RSettings changed", RSettings.settings_id, RSettings)
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

