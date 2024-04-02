import sublime
import sublime_plugin as sp
from sublime import *
from sublime_plugin import *
import typing
from typing import Optional, TypedDict, List


class History(List[str]):
    pass


class Modifiers(TypedDict):

    alt: bool
    ctrl: bool
    primary: bool
    shift: bool


class Event():

    modifier_keys: Modifiers


class RegexpSelection(sp.WindowCommand):

    # Type Hint cause error under Python 3.8.12: 
    #    TypeError 'type' object is not subscriptable
    # Python 3.8 :class:`typing.Protocol` 
    #   :pep:`544` Structural subtyping (static duck typing) 
    # Python 3.10 - PEP 604: New Type Union Operator ``X | Y``
    # use List, TypedDict ... instead of ``history: list[str] = list()``
    history: History = History()

    def run(self, regexp: str, history=0):
        if self.has_history(history):
            regexp = self.history[history]
        else:
            self.history.append(regexp)
        print("RegexpSelection run:", regexp, history)
        (res, regions) = RegexpSelection.find_all(regexp)
        view: View = self.window.active_view()
        if view:
            selection = view.sel()
            the1st = selection[0] if len(selection) else Region(0)

            # for a cursor point, not selction area
            if the1st.a == the1st.b:
                selection.clear()
                selection.add_all(iter(regions))
                return

            # convert selection for all region
            targets: list[Region] = []
            for area in selection:
                mi = min(area.a, area.b)
                mx = max(area.a, area.b)
                for it in regions:
                    if mi <= it.a < mx:
                        targets.append(it)

            # don't clear selection before you need it
            selection.clear()
            selection.add_all(targets)

            # Just for the 1st selection area
            # mi = min(the1st.a, the1st.b)
            # mx = max(the1st.a, the1st.b)
            # for it in regions:
            #     if mi < it.a < mx:
            #         selection.add(it)

    def has_history(self, index):
        if index != None and index != 0 and \
          index >= -len(self.history) and index < len(self.history):
            return self.history[index] != ""
        return False

    def input(self, args):
        print("RegexpSelection input:", args)
        regexp = args.get('regexp')
        history = args.get('history')
        last = self.has_history(history)
        if regexp == "history":
            return HistoryInputHandler()
        if (history is None or not last) and (regexp is None or regexp == ""):
            return Regexp(self.history[-1] if len(self.history) else "")

    @classmethod
    def find_all(cls, regexp: str):
        win = sublime.active_window()
        view = win.active_view()
        res: list[str] = list()
        # fmt: str = "$0"
        fmt = None
        regions: list[Region] = list()
        if view:
            regions = view.find_all(regexp, FindFlags.NONE, fmt, res)
            for it in regions[0:3]:
                res.append(view.substr(it))
        return (res, regions)


class Regexp(sp.TextInputHandler):

    def __init__(self, default: str) -> None:
        super().__init__()
        self.default = default

    # args name to transport data in command.run(self, XXX, YYY...)
    # or use super implementation:
    #     class XXXInputHandler(subime_plugin.TextInputHandler)
    def name(self) -> str:
        name = super().name()
        print("RegexpSelection name:", name)
        return name

    def placeholder(self):  # a text show as backgroud of input box in GUI
        return "Textregexp as RegexpSelection" 

    def initial_text(self):
        return self.default

    def validate(self, text: str, event: Event) -> bool:
        print("RegexpSelection validate:", text)
        return True

    def confirm(self, test: str, event: Event):
        print("RegexpSelection confirm:", event)
        return True

    def want_event(self) -> bool:
        return True

    def next_input(self, args: dict) -> Optional[CommandInputHandler]:
        regexp = args.get('regexp')
        print("RegexpSelection next_input", regexp)
        presets = [
            '\n#+ +',
            '(\\w+\\.)*(\\w+\\.?)?<[A-z<> ,?]+?>',
            '\\n\\n(?=[-+=#~.`\'"^*]{3, })([-+=#~.`\'"^*]+)\\n.+\\n\\1',
            '\\n\\n(?![-+=#~.`\'"^*]{3, }).+\\n(?=[-+=#~.`\'"^*]{3,}).+',
            '\\n\\n(?=[^-+=#~.\'"^*]{3, })[^ ]+.+\\n(?![-+=#~.\'"^*]{3, })',
            ' +def [_\\w][_\\w\\d]+ *\\(([_\\w][_\\w\\d]+,?)*\\)',
            ' *class [_\\w][_\\w\\d]+ *\\(([_\\w][_\\w\\d]+.?,?)*\\)',
            ' +class [_\\w][_\\w\\d]+ *\\(([_\\w][_\\w\\d]+.?,?)*\\)',
            ' +class [_\\w][_\\w\\d]+ *\\(([_\\w][_\\w\\d]+,?)*\\)',]
        if 'history test' == regexp:
            for it in presets:
                RegexpSelection.history.append(it)
        elif 'history' != regexp:
            return super().next_input(args)
        return HistoryInputHandler()

    def initial_selection(self) -> list:
        sel: list[tuple[int, int]] = list()
        sel.append((int(0), len(self.default)) )
        return sel

    def preview(self, text):  # return some text/html preview on GUI
        if text is None or text == "":
            return ""
        (res, regions) = RegexpSelection.find_all(text)
        his = len(RegexpSelection.history)
        hint = ("Type 'history' to review [%s]." % his) if his else ""
        return sublime.Html(
            "{}<hr><p>Matchs: {} Regions for {} ... </p>"
            .format(hint, len(regions), res))


# ImportError: cannot import name 'override' from 'typing' 
# (C:\Program Files\Sublime Text\Lib\python3.8.zip\typing.pyc)
# from typing import override, overload

class HistoryInputHandler(sp.ListInputHandler):

    # @override
    def name(self) -> str:
        return "regexp"

    # @override
    def list_items(self) -> History:
        history = RegexpSelection.history
        print("RegexSelection list_items:", history)
        return history if len(history) else History(["history list is empty"])

    # @override
    def preview(self, text) -> Html:
        (res, regions) = RegexpSelection.find_all(text)
        return sublime.Html(
            "<hr><p>Matchs: {} Regions for {} .. </p>"
            .format(len(regions), res))
