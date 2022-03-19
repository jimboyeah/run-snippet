import sublime_api as sapi
from sublime import *
from sublime_plugin import *
from datetime import datetime

##
## Context.sublime-menu config:
## [
##     {
##         "caption": "Run Snippet code",
##         "command": "run_snippet",
##         "mnemonic": "R",
##         "id": "run_snippet",
##         "keys": ["f6"], 
##     },
## ]
##

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
        return self.snippet_test()

    def message(self, content):
        msg = "⚡RS: %s" % content
        sublime.status_message(msg)
        print(msg)
        pass

    def execute_snippet(self, code):
        window = active_window()
        execpanel = window.find_output_panel("exec")
        if execpanel is None:
            execpanel = View(window.create_output_panel("exec", True))

        try:
            print("viewid: %s" % execpanel.view_id)
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
        if region.a != region.b:
            code = self.view.substr(region)
            self.code_snippets.append(code)
            self.execute_snippet(code)
        else:
            scope = self.view.scope_name(region.a)
            (a, b) = self.view.full_line(region)
            if scope.find(self.selector)<0: return None
            start = self.lookup_boundary(Region(a), "```py", min)
            end = self.lookup_boundary(Region(a), "```", max)

            if start != None and end:
                codesnippet = Region(start.b+1, end.a-1)
                code = self.view.substr(codesnippet)
                self.view.sel().add(codesnippet)
                self.execute_snippet(code)

    def lookup_boundary(self, region, tag, direction=max, maxline= 500) -> Region or None:
        a = direction(region.a, region.b)

        maxline = maxline-1
        while a>1 and (maxline)>-1:
            rgn = self.view.line(a)
            line = self.view.substr(rgn)
            a = direction(rgn.a-1, rgn.b+1)
            if line.startswith(tag): return rgn

        size = self.view.size()
        if maxline==-1 or a==direction(-1, size+1): return None


# Console Panel redirect
name = "exec" # "TestPlugin_OutputPanel"
class _LogWriter(sublime._LogWriter):

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

sys.stdout = _LogWriter()
# sys.stderr = _LogWriter()
