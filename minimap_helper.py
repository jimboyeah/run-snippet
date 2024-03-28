import sublime_plugin
import sublime

class MinimapHider(sublime_plugin.ViewEventListener):

    def __init__(self, view):
        self.view = view
        # print("helper init: ", self, view)

    def _on_modified_async(self, *args):
        win = self.view.window()
        # print(self.view, win.active_view(), self.view.size(), self.view.rowcol(self.view.size()))
        if win is not None and self.view == win.active_view():
            region = sublime.Region(0, self.view.size())
            count = self.view.rowcol(self.view.size())[0] + 1
            win.set_minimap_visible(count > 50)

    # on_hover = on_activated = on_modified_async