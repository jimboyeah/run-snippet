import sublime
import sublime_plugin as sp
from sublime import *
from sublime_plugin import *
from typing import Optional, TYPE_CHECKING


class RegexpSelection(sp.WindowCommand):

    # Java Generics: (\w+\.)*(\w+\.?)?<[A-z<> ,?]+?>
    # reStructuredText 
    # Section Title: \n\n(?=[-+=#~.`'"^*]{3, })([-+=#~.`'"^*]+)\n.+\n\1
    # Subtitle: \n\n(?![-+=#~.`'"^*]{3, }).+\n(?=[-+=#~.`'"^*]{3,}).+
    # paragraphs begin: \n\n(?=[^-+=#~.'"^*]{3, })[^ ]+.+\n(?![-+=#~.'"^*]{3, })
    # Type Hint cause error under Python 3.8: TypeError 'type' object is not subscriptable
    # def initial_selection(self) -> list[tuple[int, int]]:
    # history: list[str] = list()
    history = list()

    def run(self, regexp:str, history = 0):
        if history != 0 and history >= -len(self.history) and history < len(self.history):
            regexp = self.history[history]
        else:
            self.history.append(regexp)
        print("regexp_selection run:", regexp, history)
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

    def input(self, args):
        print("regexp_selection input:", args)
        if args.get('history') is None:
            return SimpleInputHandler(self.history[-1] if len(self.history) else "")

    def validate(self, text, event):
        print("regexp_selection validate:", event)
        return True

    def confirm(self, text, event):
        print("regexp_selection confirm:", event)
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


class SimpleInputHandler(sp.TextInputHandler):

    def __init__(self, default:str) -> None:
        super().__init__()
        self.default = default

    def name(self): # args name to transport data in command.run(...)
        return "regexp"

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
