import os
import re
import sys
from sublime import *
from sublime_plugin import *
from datetime import datetime, timedelta
from . import Settings
from .RunSnippet import Logger


class JumpToCommand(TextCommand, ViewEventListener):

    def __init__(self, *args):
        if args and isinstance(args[0], View):
            self.view = args[0]
        Logger.message("Jumpto init %s %s " % (str(args), sys.version))

    def run(self, edit, *args):
        ctx = self.parseline()
        win = self.view.window()
        if not ctx or not win:
            return
        text = ctx.text
        kind = ctx.kind
        symbol = ""

        if (kind == kindSelected) and None is re.search(r".+[\. /\\].+", text):
            symbol = "@"
        elif (kind == kindCtags):
            return self.ctags(text)
        elif (kind == kindSymbol):
            self.view.sel().clear()
            self.view.sel().add(Region(ctx.begin, ctx.end))
            win.run_command("copy",)
            win.run_command('goto_symbol_in_project', {'overlay':'goto'})
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
                return MatchArea(kindSelected, sel, region.a, region.b)

        region_of_line = self.view.line(region.a) 
        if region_of_line.a == region_of_line.b:
            return None

        line = self.view.substr(region_of_line)
        offset = region.a - region_of_line.a

        rp = line[offset:] or ""
        lp = line[0:offset] or ""

        r = rp.find("`")
        t = lp.rfind("`")
        if r >= 0 and t >= 0:
            return MatchArea(kindSymbol, line[t+1:r+offset], region.a-offset+t+1, region.a+r)

        r = rp.find("|")
        t = lp.rfind("|")
        if r >= 0 and t >= 0:
            return MatchArea(kindCtags, line[t+1:r+offset], region.a-offset+t+1, region.a+r)

        r = rp.find("]")
        t = lp.rfind("[")
        if r >= 0 and t >= 0:
            return MatchArea(kindCtags, line[t+1:r+offset], region.a-offset+t+1, region.a+r)

        r = rp.find("'")
        t = lp.rfind("'")
        if r >= 0 and t >= 0:
            return MatchArea(kindQuote, line[t+1:r+offset], region.a-offset+t+1, region.a+r)

        r = rp.find('"')
        t = lp.rfind('"')
        if r >= 0 and t >= 0:
            return MatchArea(kindQuote, line[t+1:r+offset], region.a-offset+t+1, region.a+r)

        r = rp.find(")")
        t = lp.rfind("(")
        if r >= 0 and t >= 0:
            return MatchArea(kindQuote, line[t+1:r+offset], region.a-offset+t+1, region.a+r)

        r = rp.find("*")
        t = lp.rfind("*")
        if r >= 0 and t >= 0:
            return MatchArea(kindCtags, line[t+1:r+offset], region.a-offset+t+1, region.a+r)

        t = lp.rfind(' ')
        r = rp.find(' ')
        if t == -1:
            t = 0
        if r == -1:
            r = len(rp)
        block = line[t:r+offset].strip()
        if block.startswith("http") or block.startswith("file://"):
            return MatchArea(kindBlock, block, region.a-offset+t+1, region.a+r)
        else:
            return MatchArea(kindSpaced, block, region.a-offset+t+1, region.a+r)

# def plugin_loaded() -> None:
#     print("plugin loaded")


# def plugin_unloaded() -> None:
#     print("plugin unloaded")


class MatchKind: 
    def __init__(self, kind:str):
        self.kind = kind


kindSpaced = MatchKind('Spaced')
kindBlock = MatchKind('Block')
kindText = MatchKind('Text')
kindFile = MatchKind('File')
kindSymbol = MatchKind('Symbol')
kindSelected = MatchKind('Selected')
kindQuote = MatchKind('Quote')
kindCtags = MatchKind('Ctags')


class MatchArea:

    def __init__(self, kind: MatchKind, text: str, begin: int, end: int):
        self.kind = kind
        self.text = text
        self.begin = begin
        self.end = end

    def toString(self):
        return r'<MatchArea kind=%s text=%s [%d,%d]>' % (
            self.kind, self.text, self.begin, self.end)
