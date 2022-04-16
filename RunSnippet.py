import re
import sublime_api as sapi
from sublime import *
from sublime_plugin import *
from datetime import datetime

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

    def jump(self, file):
        if file:
            self.view.window().run_command("show_overlay", 
            {"overlay":"goto", "show_file": True, "text":file.replace("\\","/")})

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
        rng = self.view.sel()[0]
        if rng.a != rng.b:
            sel = self.view.substr(rng)
            if len(sel.split("\n"))==1:
                return sel
        rnl = self.view.line(rng.a)
        if rnl.a == rnl.b:
            return None

        line = self.view.substr(rnl)
        point = rng.a - rnl.a

        rp = line[point:] or ""
        lp = line[0:point] or ""

        r = rp.find("'")
        l = lp.rfind("'")
        if r>=0 and l>=0 :
            return line[l+1:r+point]

        r = rp.find('"')
        l = lp.rfind('"')
        if r>=0 and l>=0 :
            return line[l+1:r+point]

        r = rp.find(")")
        l = lp.rfind("(")
        if r>=0 and l>=0 :
            return line[l+1:r+point]

        l = lp.find(' ')
        if l==1:
            return line[l+1:].strip()
            
        print(lp, "<===>" , rp)


class RunSnippetCommand(TextCommand):
    __dict__ = ['lang_type','code_snippets']
    selector = "source.python"

    def __init__(self, view):
        self.view = view
        pass

    def run(self, edit):
        self.snippet_test(True)
        # self.view.insert(edit, 0, "Hello, RunSnipetCommand!")
        pass

    def is_enabled(self, *args):
        Logger.message("is_enabled(self, edit):")
        return self.snippet_test()

    def execute_snippet(self, code):
        window = active_window()
        execpanel = window.find_output_panel("exec")
        if execpanel is None:
            execpanel = View(window.create_output_panel("exec", True))

        try:
            # print("viewid: %s" % execpanel.view_id)
            execpanel.settings().set("auto_indent", False)
            execpanel.sel().clear()
            execpanel.sel().add(Region(0))
            execpanel.run_command("insert", {"characters":"""\n%s\n""" % ("⚡" * 40)})
            # code = compile(code, "string", "exec")
            exec(code)
        except Exception as ex:
            print("execute_snippet error: %s" % ex)
            # print("execute_snippet error: {0}".format(ex))
            # print(f"tb: {ex.__traceback__}")
            raise

    def snippet_test(self, execute=False):
        regionset = self.view.sel()
        self.code_snippets = []

        for region in regionset:
            scope = self.view.scope_name(region.a)
            if scope.find(self.selector)>-1:
                if not execute: return True
                self.snippet_region(region)
        return False

    def snippet_region(self, region):
        scope = self.view.scope_name(region.a)
        if region.a != region.b:
            code = self.view.substr(region)
            self.code_snippets.append(code)
            self.execute_snippet(code)
        elif scope=="source.python":
            code = self.view.substr(Region(1, self.view.size()))
            self.execute_snippet(code)
        else:
            (a, b) = self.view.full_line(region)
            if scope.find(self.selector)<0: return None
            start = self.lookup_boundary(Region(a), "```py", min)
            end = self.lookup_boundary(Region(a), "```", max)

            if start != None and end:
                codesnippet = Region(start.b+1, end.a-1)
                code = self.view.substr(codesnippet)
                self.view.sel().add(codesnippet)
                self.execute_snippet(code)

    def lookup_boundary(self, region, tag, direction=max, maxline= 300) -> Region or None:
        a = direction(region.a, region.b)

        maxline = maxline-1
        while a>1 and (maxline)>-1:
            rgn = self.view.line(a)
            line = self.view.substr(rgn)
            a = direction(rgn.a-1, rgn.b+1)
            if line.startswith(tag): return rgn
            maxline -= 1

        size = self.view.size()
        if maxline==-1 or a==direction(-1, size+1): return None


# Console Panel redirect
name = "exec" # "TestPlugin_OutputPanel"
class Logger(sublime._LogWriter):

    def message(content):
        msg = "⚡RS: %s" % content
        sublime.status_message(msg)
        pass

    def write(self, s):
        super().write(s)
        # if '\n' in s or '\r' in s:
            # return # sapi.status_message("⚠ console output flush")

        window_id = sapi.active_window()
        unlisted = True
        panel_id = sapi.window_find_output_panel(window_id, name)
        panel_view = View(panel_id) if panel_id else \
            View(sapi.window_create_output_panel(window_id, name, unlisted))

        panel_view.settings().set("auto_indent", False)
        panel_view.sel().clear()
        panel_view.sel().add(Region(0))

        timestamp = datetime.today().strftime("%H:%M::%S")
        console_output = s.replace("/n/n", "\n")
        # --===== 👉TestPlugin Output Panel {panel_view}👈 =====---
        # =================== {timestamp} ===================
        panel_view.run_command('insert', {'characters': console_output})

# sys.stdout = Logger()
# sys.stderr = Logger()
