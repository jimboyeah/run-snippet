import os
import re
import sys
import json
from sublime import *
from sublime_plugin import *
from datetime import datetime, timedelta

from . import Settings
from .RunSnippet import Logger



class JumpToCommand(TextCommand, ViewEventListener):

    def __init__(self, *args):
        if args and isinstance(args[0], View):
            self.view = args[0]
        # print("init JumpTo %s ===" % (str(args)))
        Logger.message("init %s" % str(args))

    # Ctrl+P        show_overlay: goto, "show_files": true
    # Ctrl+R        show_overlay: goto, "text": "@"
    # Ctrl+G        show_overlay: goto, "text": ":"
    # Ctrl+;        show_overlay: goto, "text": "#"
    # F12           goto_definition
    # Ctrl+Shift+P  show_overlay: command_palette
    def run(self, edit, *args):
        ctx = self.parseline()
        win = self.view.window()
        if not ctx or not win:
            return
        text = ctx.text
        kind = ctx.kind
        symbol = ""
        if isinstance(kind, MatchKindSelected) and None is re.search(r".+[\. /\\].+", text):
            symbol = "@"
        elif isinstance(kind, MatchKindCtags):
            return self.ctags(text)
        elif isinstance(kind, MatchKindSymbol):
            print(ctx.toString())
            self.view.sel().clear()
            self.view.sel().add(Region(ctx.begin, ctx.end))
            win.run_command("copy",)
            win.run_command('goto_symbol_in_project', {'overlay':'goto'}) # `run`
            return win.run_command('paste',)
            # "goto_definition", {"side_by_side": True, "clear_to_right": True} )
        elif text.startswith("http") or text.startswith("file://"):
            return os.popen("start %s" % text)
        elif text.startswith("#"):
            hash = re.sub(r'[-_#]', lambda x: ' ', text)
            return win.run_command(
                'show_overlay',
                {'overlay': 'goto', 'text': '@'+hash})

        for it in range(0, win.num_groups()):
            (between, rs) = Settings.get("jump_between_group")
            print(("jump_between_group"), between, rs.settings_id)
            if not between:
                break
            grouped = win.views_in_group(it)
            if self.view in grouped:
                continue
            win.focus_group(it)

        text = symbol+text.replace("\\", "/")
        win.run_command(
            "show_overlay",
            {"overlay": "goto", "show_file": True, "text": text})

    """
    Vim CTags in-file jumping

    1. Setting options          |set-option|
    1. Setting options          *set-option* *E764*

    more for test ...           *set-option* *E764*
    """
    keyword1st = "keyword"
    lasttime = datetime.now()
    duration = timedelta(microseconds=200000)

    def ctags(self, ctag):

        if not isinstance(ctag, str): 
            return False

        doublejump = datetime.now() - self.lasttime < self.duration
        if self.keyword1st != ctag or doublejump:
            self.keyword1st = ctag
            tags = "[*]{0}[*]".format(ctag)
            region = self.view.find(tags, 0, IGNORECASE)
            cur = self.view.sel()[0]
            if not region.a < cur.a < region.b:
                self.view.sel().add(region.a+1)
                return self.view.show_at_center(region)

        self.lasttime = datetime.now()
        tags = r"(\*|\|){0}\1|\[{0}\]".format(ctag)
        sets = self.view.find_all(tags, IGNORECASE)
        rgn = self.view.sel()[0]

        # where I can find the keyboard modifier? 
        # I need it to reverse the backward direction.
        for it in sets:
            if it.b < rgn.a or it.a <= rgn.a <= it.b:
                if sets[-1] != it:
                    continue
                it = sets[0]
            self.view.sel().subtract(rgn)
            self.view.sel().add(it.a+1)
            self.view.show_at_center(it)
            break

    def is_enabled(self, *args):
        Logger.message("jump to is_enabled %s" % str(args))
        return self.parseline() is not None

    def parseline(self):

        sel = self.view.sel()
        if len(sel) == 0:
            return
        region = sel[0]

        if region.a != region.b:
            sel = self.view.substr(region)
            if len(sel.split("\n")) == 1:
                return MatchArea(MatchKindSelected(), sel, region.a, region.b)

        region_of_line = self.view.line(region.a) 
        if region_of_line.a == region_of_line.b:
            return None

        line = self.view.substr(region_of_line)
        offset = region.a - region_of_line.a

        rp = line[offset:] or ""
        lp = line[0:offset] or ""

        r = rp.find("|")
        t = lp.rfind("|")
        if r >= 0 and t >= 0:#`abcde`
            return MatchArea(MatchKindCtags(), line[t+1:r+offset], region.a-offset+t+1, region.a+r)

        r = rp.find("]")
        t = lp.rfind("[")
        if r >= 0 and t >= 0:
            return MatchArea(MatchKindCtags(), line[t+1:r+offset], region.a-offset+t+1, region.a+r)

        r = rp.find("'")
        t = lp.rfind("'")
        if r >= 0 and t >= 0:
            return MatchArea(MatchKindQuote(), line[t+1:r+offset], region.a-offset+t+1, region.a+r)

        r = rp.find('"')
        t = lp.rfind('"')
        if r >= 0 and t >= 0:
            return MatchArea(MatchKindQuote(), line[t+1:r+offset], region.a-offset+t+1, region.a+r)

        r = rp.find(")")
        t = lp.rfind("(")
        if r >= 0 and t >= 0:
            return MatchArea(MatchKindQuote(), line[t+1:r+offset], region.a-offset+t+1, region.a+r)

        r = rp.find("`")
        t = lp.rfind("`")
        if r >= 0 and t >= 0:
            return MatchArea(MatchKindSymbol(), line[t+1:r+offset], region.a-offset+t+1, region.a+r)

        r = rp.find("*")
        t = lp.rfind("*")
        if r >= 0 and t >= 0:
            return MatchArea(MatchKindCtags(), line[t+1:r+offset], region.a-offset+t+1, region.a+r)

        t = lp.find(' ')
        if t == 1:
            return MatchArea(MatchKindSpaced(), line[t+1:r+offset], region.a-offset+t+1, region.a+r)

        t = lp.rfind(' ')
        r = rp.find(' ')
        if t == -1:
            t = 0
        if r == -1:
            r = len(rp)
        block = line[t:r+offset].strip()
        if block.startswith("http") or block.startswith("file://"):
            return MatchArea(MatchKindBlock(), block, region.a-offset+t+1, region.a+r)
        else:
            return MatchArea(MatchKindSpaced(), block, region.a-offset+t+1, region.a+r)

# def plugin_loaded() -> None:
#     print("plugin loaded")


# def plugin_unloaded() -> None:
#     print("plugin unloaded")

class MatchKind: pass
class MatchKindSpaced (MatchKind): pass
class MatchKindBlock (MatchKind): pass
class MatchKindText (MatchKind): pass
class MatchKindFile (MatchKind): pass
class MatchKindSymbol (MatchKind): pass
class MatchKindSelected (MatchKind): pass
class MatchKindQuote (MatchKind): pass
class MatchKindCtags (MatchKind): pass

class MatchArea:

    def __init__(self, kind:MatchKind, text:str, begin:int, end:int):
        self.kind = kind
        self.text = text
        self.begin = begin
        self.end = end

    def toString(self):
        return r'<MatchArea kind=%s text=%s [%d,%d]>' % (self.kind, self.text, self.begin, self.end)