import os
import re
import sys
import pathlib
import tempfile
import sublime_api as sapi
from sublime import *
from sublime_plugin import *
from datetime import datetime, timedelta


class RunSnippetCommand(TextCommand):
    __dict__ = ['lang_type', 'code_snippets']
    coderegion = None
    selectorActive = None
    selectors = { 
        "source.bash": "execute_bash",
        "source.shell.bash": "execute_bash",
        "markup.raw.block.markdown": "execute_bash",
        "text.restructured": "execute_bash",
        "source.dosbatch": "execute_cmd",
        # "text.html.markdown": "execute_bash",
        "source.python": "execute_py",
        }

    def __init__(self, view):
        self.view = view
        pass
        # scope_name

    def run(self, edit):
        if self.selectorActive is None or self.coderegion is None:
            return

        method = getattr(self, self.selectors[self.selectorActive], None)
        print("run snippet agent", self.selectorActive, self.coderegion, method)
        if method and isinstance(method, type(self.run)):
            method(self.coderegion)

    def is_enabled(self, *args):
        ok = self.snippet_test()
        Logger.message("RunSnippet is_enabled(self, edit): %s" % ok)
        return ok 

    def execute_cmd(self, region: Region):
        Logger.message("RunSnippet not yet support: %s" % self.selectorActive)

    def exit_status(self, exitcode: int):
        status = {
            '0': 'Successfully execute.',
            '1': 'Catchall for general errors',
            '2': 'Misuse of shell builtins',
            '126': 'Command invoked cannot execute',
            '127': '"command not found"',
            '128': 'Invalid argument to exit',
            '128+': 'Fatal error signal "%s"' % exitcode,
            '130': 'Script terminated by Control-C',
            '255': 'Exit status out of range',
            }
        if status.get(str(exitcode)):
            return status[str(exitcode)]
        elif 128 < exitcode < 255:
            return status['128+']

        return status['255']

    def execute_bash(self, region: Region):
        view = self.view

        code = view.substr(region) or view.substr(view.line(region))
        # regex = re.compile('^#.*\n', re.RegexFlag.MULTILINE)
        # code = regex.sub('', code).replace(';;', ';')
        tmp = tempfile.mktemp(".sh", "runsnippet-")
        file = open(tmp, 'w')
        file.writelines(code)
        cwd = pathlib.Path(view.file_name() or ".").parent
        print("bash@%s: [%s] %s\n" % (cwd, region, tmp), code[0:140], "...")

        (arg, shell) = ("/c", "C:/Windows/System32/cmd.exe")
        (arg, shell) = ("-c", "C:/msys64/usr/bin/bash.exe")
        env = {"PATH": "C:/msys64/usr/bin/"}

        # os.execlp('bash', '-c', code) # this method will cause Sublime plugin-host exit.
        # ecode = os.system("bash -c '%s ; sleep 3'" % code)
        # for cmd shell
        # pid = os.spawnle(os.P_NOWAIT, shell, "'%s %s'" %(arg, code), env)
        # pid = os.spawnve(os.P_NOWAIT, shell, ["'%s %s'" %(arg, code)], env)
        # for bash shell
        os.chdir(cwd)
        pid = os.spawnv(os.P_NOWAIT, shell, [shell, tmp])
        # print("bash shell return:", self.exit_status(pid))
        # pid = os.spawnv(os.P_NOWAIT, shell, [shell, arg, "'%s'" %(code)])
        # pid = os.spawnle(os.P_NOWAIT, shell, shell, arg, "'%s'" %(code), env)
        # pid = os.spawnve(os.P_NOWAIT, shell, [shell, arg, "'%s'" % (code)], env)
        # excode = os.spawnv(os.P_WAIT, shell, [shell, arg, "'%s"%(code)])
        # print("exit code: ", shell, arg, excode)
        # (pid, ecode_shift8) = os.waitpid(pid, 0)
        # print("exit code: ", shell, arg, pid, ecode_shift8>>8)

    def execute_py(self, region: Region):
        scope = self.selectorActive
        window = active_window()
        view = self.view
        code = view.substr(self.coderegion)

        # execpanel = window.find_output_panel("exec")
        # if execpanel is None:
        #    execpanel = View(window.create_output_panel("exec", True))
        execpanel = window.create_output_panel("exec", True)

        try:
            print("execute_py: [%s]" % scope, self.coderegion, code)
            execpanel.settings().set("auto_indent", False)
            execpanel.sel().clear()
            execpanel.sel().add(Region(0))
            print(repr(execpanel))
            # execpanel.run_command("insert", {"characters": "\n%s\n" % ("⚡" * 40)})
            # code = compile(code, "string", "exec")
            # execpanel.run_command("insert", {"characters": str(exec(code))})
            oldout = sys.stdout
            sys.stdout = Logger()
            exec(code)
            sys.stdout = oldout
        except Exception as ex:
            print("execute_py error: %s" % ex)
            # print("execute_py error: {0}".format(ex))
            # print(f"tb: {ex.__traceback__}")
            raise

    def snippet_test(self, execute=False):
        regionset = self.view.sel()
        self.code_snippets = []

        for region in regionset:
            scope = self.view.scope_name(region.a)
            for it in self.selectors:
                if scope.find(it) > -1:
                    print("RunSnippet scope test:", it)
                    self.selectorActive = it
                    self.coderegion = self.expansion_region(self.selectorActive, region)
                    if not execute:
                        return True
        self.selectorActive = None
        return False

    def expansion_region(self, scope: str, region: Region, increment=False):
        view = self.view

        while region.a > 0:
            expansion = view.line(region.a-1)
            if view.scope_name(expansion.a).find(scope) == -1:
                break
            region.a = expansion.a

        while region.b < view.size():
            expansion = view.line(region.b+1)
            if view.scope_name(expansion.b).find(scope) == -1:
                break
            region.b = expansion.b

        if increment:
            view.sel().add(region)

        return region


# Console Panel redirect
name = "exec"  # "TestPlugin_OutputPanel"


class Logger(sublime._LogWriter):

    @classmethod
    def message(cls, content:str):
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
