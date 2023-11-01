import sublime
import sublime_plugin as sp
from sublime import *
from sublime_plugin import *

class RegexpSelection(sp.WindowCommand):

    def run(self, regexp:str):
        print("regexp_selection run:", regexp, self.window)
        (res, regions) = RegexpSelection.find_all(regexp)
        view = self.window.active_view()
        if view:
            view.sel().clear()
            view.sel().add_all(iter(regions))

    def input(self, args):
        print("regexp_selection input:", args)
        return SimpleInputHandler()

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

    def name(self): # args name to transport data in command.run(...)
        return "regexp"

    def placeholder(self): # a text show as backgroud of input box in GUI
        return "Text as RegexpSelection" 

    def preview(self, text): # return some text/html preview on GUI
        if text is None or text == "":
            return ""
        (res, regions) = RegexpSelection.find_all(text)
        return sublime.Html("<H3>Matchs: {} Regions for {}</H3>"
            .format(len(regions), res))
