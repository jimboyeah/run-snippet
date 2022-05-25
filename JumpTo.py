import os
import re
import sys
import sublime_api as sapi
from sublime import *
from sublime_plugin import *
from datetime import datetime, timedelta

from . import Settings
from .RunSnippet import Logger

'''
Config Context.sublime-menu and sbulime-keymap:
[
    {
        "caption": "Run Snippet code",
        "command": "run_snippet",
        "mnemonic": "R",
        "id": "run_snippet",
        "keys": ["f6"], 
    },
        {
        "caption": "Jupm to ...",
        "command": "jump_to",
        "mnemonic": "j",
        "id": "jump_to",
        "keys": ["f9"], 
    },
]

- language-reference\builtin-types\value-types.md
- language-reference/builtin-types/value-types.md
- [`is` expression](operators/is.md)
# csharp\fundamentals\functional\pattern-matching.md
:::code language="csharp" source="Program.cs" ID="NullableCheck":::

- md/sublime.md
- RunSnippet/readme.md
- RunSnippet/JumpTo.py
- RunSnippet/UnicodeSymbols.py
- Lib/python33/sublime.py
- Lib/python33/sublime_plugin.py
- Lib/python38/sublime.py
- Lib/python38/sublime_plugin.py
- User/RunSnippet.sublime-settings
- RunSnippet/material/vim_flavor.md
- RunSnippet/material/bash.5.1.md
- RunSnippet/material/linux_cli_script_bible.md
'''

class JumpToCommand(TextCommand, ViewEventListener):

    def __init__(self, *args):
        if args and isinstance(args[0], View):
            self.view = args[0]
        # print("init JumpTo %s ===" % (str(args)))
        Logger.message("init %s" % str(args))

    def run(self, edit, *args):
        # Logger.message("JumpToCommand %s" % str(args))
        file = self.parseline()
        self.jump(file)

    # Ctrl+P        show_overlay: goto, "show_files": true
    # Ctrl+R        show_overlay: goto, "text": "@"
    # Ctrl+G        show_overlay: goto, "text": ":"
    # Ctrl+;        show_overlay: goto, "text": "#"
    # F12           goto_definition
    # Ctrl+Shift+P  show_overlay: command_palette
    def jump(self, file):
        if not file: return;
        text = file["text"]
        kind = file["kind"]
        symbol = ""
        if kind == "selected" and None == re.search(r".+[\. /\\].+", text):
            symbol = "@"
        elif kind == "ctags":
            return self.ctags(text)
        elif text.startswith("http") or text.startswith("file://"):
            return os.popen("start %s" % text)
        elif text.startswith("#"):
            hash = re.sub(r'[-_#]',lambda x: ' ', text)
            return self.view.window().run_command('show_overlay',
                {'overlay':'goto', 'text':'@'+hash})

        for it in range(0, self.view.window().num_groups()):
            print("RSttings", Settings.RSettings.settings_id, Settings.RSettings)
            (between, rs) = Settings.get("jump_between_group")
            print(("jump_between_group"), between, rs.settings_id)
            if not between: break
            grouped = self.view.window().views_in_group(it)
            if self.view in grouped:
                continue
            self.view.window().focus_group(it)
            # self.view.window().active_group()
            # self.view.window().active_view_in_gorup(it)

        self.view.window().run_command("show_overlay", 
        {"overlay":"goto", "show_file": True, "text": symbol+text.replace("\\","/")})

    """
    Vim CTags in-file jumping

    1. Setting options          |set-option|
    1. Setting options          *set-option* *E764*
    
    more for test ...           *set-option* *E764*
    """
    keyword1st = "keyword"
    lasttime = datetime.now()
    duration = timedelta(microseconds=300000)
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
        tags = "[|]{0}[|]|[*]{0}[*]".format(ctag)
        sets = self.view.find_all(tags, IGNORECASE)
        # self.view.sel().add_all(sets)
        rgn = self.view.sel()[0]

        # where I can find the keyboard modifier? 
        # I need it to reverse the backward direction.
        for it in sets: 
            if it.b < rgn.a or it.a <= rgn.a <= it.b: 
                if sets[-1] != it: continue
                it = sets[0]
            self.view.sel().add(it.a+1)
            self.view.sel().subtract(rgn)
            self.view.show_at_center(it)
            break

    def is_enabled(self, *args):
        Logger.message("jump to is_enabled %s" % str(args))
        return self.parseline() != None

    # def on_post_text_command(self, action, extras):
    #     Logger.message("jump to: %s %s" % (action, str(extras)))
    #     if action == "drag_select" and extras and 'extend' in extras:
    #         file = self.parseline()
    #         Logger.message("jump to: %s" % (file))
    #         self.jump(file)

    def parseline(self):
        sel = self.view.sel()
        rng = len(sel) and sel[0]

        if rng.a != rng.b:
            sel = self.view.substr(rng)
            if len(sel.split("\n"))==1:
                return {"kind":"selected", "text": sel}
        rnl = self.view.line(rng.a)
        if rnl.a == rnl.b:
            return None

        line = self.view.substr(rnl)
        point = rng.a - rnl.a

        rp = line[point:] or ""
        lp = line[0:point] or ""

        r = rp.find("|")
        l = lp.rfind("|")
        if r>=0 and l>=0 :
            return {"kind":"ctags", "text": line[l+1:r+point]}

        r = rp.find("]")
        l = lp.rfind("[")
        if r>=0 and l>=0 :
            return {"kind":"ctags", "text": line[l+1:r+point]}

        r = rp.find("'")
        l = lp.rfind("'")
        if r>=0 and l>=0 :
            return {"kind":"quote", "text": line[l+1:r+point]}

        r = rp.find('"')
        l = lp.rfind('"')
        if r>=0 and l>=0 :
            return {"kind":"quote", "text": line[l+1:r+point]}

        r = rp.find(")")
        l = lp.rfind("(")
        if r>=0 and l>=0 :
            return {"kind":"quote", "text": line[l+1:r+point]}

        r = rp.find("`")
        l = lp.rfind("`")
        if r>=0 and l>=0 :
            return {"kind":"quote", "text": line[l+1:r+point]}

        r = rp.find("*")
        l = lp.rfind("*")
        if r>=0 and l>=0 :
            return {"kind":"ctags", "text": line[l+1:r+point]}

        l = lp.find(' ')
        if l==1:
            return {"kind":"spaced", "text": line[l+1:].strip()}

        l = lp.rfind(' ')
        r = rp.find(' ')
        if l == -1: l = 0
        if r == -1: r = len(rp)
        block = line[l:r+point].strip()
        if block.startswith("http") or block.startswith("file://"):
            return {"kind":"block", "text": block}
        else:
            return {"kind":"spaced", "text": block}
        
        print(lp, "<===>" , rp)
