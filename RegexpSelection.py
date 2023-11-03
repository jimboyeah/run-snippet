import sublime
import sublime_plugin as sp
from sublime import *
from sublime_plugin import *
import typing
from typing import Optional, TypedDict, List


class History(List[str]):
    pass


class RegexpSelection(sp.WindowCommand):

    # Type Hint cause error under Python 3.8.12: TypeError 'type' object is not subscriptable
    # Python 3.8 :class:`typing.Protocol` :pep:`544` Structural subtyping (static duck typing) 
    # Python 3.10 - PEP 604: New Type Union Operator ``X | Y``
    # use List, TypedDict ... instead of ``history: list[str] = list()``
    history: History = History()

    def run(self, regexp:str, history = 0):
        if self.has_history(history):
            regexp = self.history[history]
        else:
            self.history.append(regexp)
        print("RegexpSelection run:", regexp, history)
        (res, regions) = RegexpSelection.find_all(regexp)
        view = self.window.active_view()
        if view:
            selection = view.sel()
            the1st = selection[0] if len(selection) else Region(0)
            selection.clear()
            if the1st.a == the1st.b:
                selection.add_all(iter(regions))
                return

            mi = min(the1st.a, the1st.b)
            mx = max(the1st.a, the1st.b)
            for it in regions:
                if mi < it.a < mx:
                    selection.add(it)

    def has_history(self, index):
        if index != None and index != 0 and \
          index >= -len(self.history) and index < len(self.history):
            return self.history[index] != ""
        return False

    def input(self, args):
        print("RegexpSelection input:", args)
        regexp = args.get('regexp')
        history = args.get('history')
        args['regexp'] = "rewrited"
        last = self.has_history(history)
        if (history is None or not last ) and (regexp is None or regexp == ""):
            return RegexpInputHandler(self.history[-1] if len(self.history) else "")

    def validate(self, text: str) -> bool:
        print("RegexpSelection validate:", text)
        return True

    def confirm(self, *event):
        print("RegexpSelection confirm:", event)
        return True

    def want_event(self) -> bool:
        return True

    @classmethod
    def find_all (cls, regexp: str):
        win  = sublime.active_window()
        view = win.active_view()
        res: list[str] = list()
        fmt: str = "$0"
        regions: list[Region] = list()
        if view:
            regions = view.find_all(regexp, FindFlags.NONE, fmt, res  )
        return (res, regions)


class RegexpInputHandler(sp.TextInputHandler):

    def __init__(self, default:str) -> None:
        super().__init__()
        self.default = default


    # args name to transport data in command.run(self, XXX, YYY...)
    # or use super implementation:
    #     class XXXInputHandler(subime_plugin.TextInputHandler)
    def name(self) -> str:
        name = super().name()
        print("RegexpSelection name:", name)
        return name

    def placeholder(self): # a text show as backgroud of input box in GUI
        return "Text as RegexpSelection" 

    def initial_text(self):
        return self.default

    def next_input(self, args) -> Optional[CommandInputHandler]:
        print("RegexpSelection next_input", args)
        return super().next_input(args)

    def initial_selection(self) -> list:
        sel: list[tuple[int, int]] = list()
        sel.append( (int(0), len(self.default)) )
        return sel

    def preview(self, text): # return some text/html preview on GUI
        if text is None or text == "":
            return ""
        (res, regions) = RegexpSelection.find_all(text)
        return sublime.Html("<hr><p>Matchs: {} Regions for {} ... </p>"
            .format(len(regions), res[0:3]))
