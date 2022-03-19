
## ==⚡ RunSnippetCommand 插件

作为一个重度 Sublime Text 用户，掌握 Plugin-host 插件机制及插件开发是非常必要的，有些稀奇古怪的想法功能都可以实现。

在 MD 文档中执行 Python 代码片段，比如 MD 文档中有以下代码片段，按注解提示配置好插件上下文菜单，保持光标在代码块上，按 F6 就可以执行：

```py
import sys
import datetime

'''
Context.sublime-menu config for RunSnippetCommand:
[
    {
        "caption": "Run Snippet code",
        "command": "run_snippet",
        "mnemonic": "R",
        "id": "run_snippet",
        "keys": ["f6"], 
    },
    {
        "caption": "Open Result Panel",
        "keys": ["shift+escape"], "command": "show_panel",
        "args": {"panel": "output.exec"},
        "context": [ { "key": "panel_visible", "operand": true } ]
    },
]
'''

newline = ("\n    ** ")

print(datetime.datetime.now())
print("*" * 80)
print(newline+newline.join(sys.path))
print("*" * 80)

# print(f'''
#   {datetime.datetime.now()}
#   {"*" * 80}
#   ** {newline.join(sys.path)}
#   {"*" * 80}
#   ''')
```

可以在 Packages 目录执行以下命令安装 RunSnippet 插件：

    git clone git@github.com/jimboyeah/run-snippet.git


Sublime Text 4 插件宿主支持 Python 3.3、3.8，但在 Packages 目录安装的插件默认是 Plugin-Host 3.3，某些 Python 3.8 新功能不能使用。

RunSnippetCommand 插件实现代码，以下是基于 Python 3.8 的语法，可以根据 Sublime 选择器实现更多语言的支持，包括 C/C++，只需要配置好编译器待调用即可：


```py
import sublime_api as sapi
from sublime import *
from sublime_plugin import *


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
        msg = f"⚡RS: {content}"
        sublime.status_message(msg)
        print(msg)
        pass

    def execute_snippet(self, code):
        window = active_window()
        execpanel = window.find_output_panel("exec")
        if execpanel is None:
            execpanel = View(window.create_output_panel("exec", True))

        execpanel.settings().set("auto_indent", False)
        execpanel.sel().clear()
        execpanel.sel().add(Region(0))
        execpanel.run_command("insert", {"characters":f"""\n{"⚡" * 40}\n"""})
        try:
            # code = compile(code, "string", "exec")
            exec(code)
        except Exception as ex:
            print(f"execute_snippet error: {ex=}")
            # print(f"tb: {ex.__traceback__}")
            raise

    def snippet_test(self, execute=False):
        regionset = self.view.sel()
        self.code_snippets = []

        for region in regionset:
            scope:str = self.view.scope_name(region.a)
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
            scope:str = self.view.scope_name(region.a)
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

        while a>1 and (maxline:=maxline-1)>-1:
            rgn = self.view.line(a)
            line = self.view.substr(rgn)
            a = direction(rgn.a-1, rgn.b+1)
            if line.startswith(tag): return rgn

        size = self.view.size()
        if maxline==-1 or a==direction(-1, size+1): return None
```


## ==⚡ Sublime API 探索
- https://docs.sublimetext.io/guide/extensibility/plugins/
- https://docs.sublimetext.io/reference/plugins.html
- https://docs.sublimetext.io/reference/python_api.html
- https://docs.sublimetext.io/reference/key_bindings.html
- https://www.sublimetext.com/docs/3/api_reference.html
- Package Control https://packagecontrol.io/docs

将 Python 脚本放到 Sublime 安装包目录下就可以被插件管理器加载执行，可以使用以下脚本测试脚本解析器的版本及位置，并且最简单的插件只需要继承指定的类型就只可以实现：

```py
import sys
import sublime
import sublime_api

print("👉 Sublime Text Plugin Test - Python Script 👈")
if sys.version_info >= (3,6):
    print(
    f"    Module Name: {__name__}\n"
    f" Python Version: {sys.version}\n"
    f"   Version Info: {sys.version_info}\n"
    f"    Interpreter: {sys.executable}\n"
    f"   Sublime Text: {sublime.version()}\n"
    f"     Below 3.9?: {(3,9)>sys.version_info}\n"
    f"Type of version_info: {type(sys.version_info)}\n"
    f"Is version_info type of tuple: {isinstance(sys.version_info, tuple)}\n"
    f"sublime_api.version()                : {sublime_api.version()}\n"
    f"sublime_api.platform()               : {sublime_api.platform()}\n"
    f"sublime_api.architecture()           : {sublime_api.architecture()}\n"
    f"sublime_api.channel()                : {sublime_api.channel()}\n"
    f"sublime_api.executable_path()        : {sublime_api.executable_path()}\n"
    f"sublime_api.packages_path()          : {sublime_api.packages_path()}\n"
    f"sublime_api.installed_packages_path(): {sublime_api.installed_packages_path()}\n"
    f"sublime_api.cache_path()             : {sublime_api.cache_path()}\n"
    )
else:
    print("\n".join((
    " Python Version: %s" % str(sys.version), 
    "    Interpreter: %s" % sys.executable,
    "   Sublime Text: %s" % str(sublime.version()),
    )))
if sys.version_info >= (3,8):
    print(
    f"Byte-Code Cache  {sys.pycache_prefix}\n"
    )
```

    >> Output:
    👉 Sublime Text Plugin Test - Python Script 👈
        Module Name: User.TestPlugin
     Python Version: 3.8.8 (default, Mar 10 2021, 13:30:47) [MSC v.1915 64 bit (AMD64)]
       Version Info: sys.version_info(major=3, minor=8, micro=8, releaselevel='final', serial=0)
        Interpreter: C:\Program Files\Sublime Text 3\plugin_host-3.8.exe
       Sublime Text: 4121
         Below 3.9?: True
    Type of version_info: <class 'sys.version_info'>
    Is version_info type of tuple: True
    sublime_api.version()                : 4121
    sublime_api.platform()               : windows
    sublime_api.architecture()           : x64
    sublime_api.channel()                : stable
    sublime_api.executable_path()        : C:\Program Files\Sublime Text 3\sublime_text.exe
    sublime_api.packages_path()          : C:\Users\UserName\AppData\Roaming\Sublime Text 3\Packages
    sublime_api.installed_packages_path(): C:\Users\UserName\AppData\Roaming\Sublime Text 3\Installed Packages
    sublime_api.cache_path()             : C:\Users\UserName\AppData\Local\Sublime Text 3\Cache
    Byte-Code Cache  C:\Users\UserName\AppData\Local\Sublime Text 3\Cache\__pycache__

因为 Python 运行时会先将脚本编译生成字节码再执行，所以开发插件时，可能因为文件经常改动导致原有的类型还存在字码文件中，但是最新的状态应该是删除掉的，这可以能导致一些难以发现的根源的问题。

可以重启或清理 Sublime Text 插件宿主程序生成的临时文件。

了解决 Sublime Text API 的基本框架，核心是 sublime_api 模块，它是 Plugin Host 导出的非开源 API 接口，基于这套开发插件。并且 Sublime Text 官方提供的插件 API 框架也是基于 sublime_api 整理的一套 Python 类框架。


### ===🗝 Windows、View、Sheet 关系

每个 Sublime 程序都可以创建多个窗口，也就是系统任务中看到的窗口，每个窗口包含多个 View，它与 Sheet 关联，不同类型的 Sheet 子类形，对应不同的内容格式，有 TextSheet、ImageSheet、HtmlSheet。

可以使用 Window 对象的 new_file() 方法创建一个 View，默认为 TextSheet 内容格式，当然，最后还是回到 sublime_api 展出的接口。

```py
    def new_html_sheet(self, name, contents, flags=0, group=-1):
        return make_sheet(sublime_api.window_new_html_sheet(
            self.window_id, name, contents, flags, group))


    def new_file(self, flags=0, syntax=""):
        """ flags must be either 0 or TRANSIENT """
        return View(sublime_api.window_new_file(self.window_id, flags, syntax))


    sublime_api.html_sheet_set_contents(self.sheet_id, contents)
```

以下代码演示了 Windows、View、Sheet 等对象是如何关联的，这些类对象是主程序界面的类型代表：

```py
import sys
import sublime
import sublime_api

# Window and View API
windows= sublime.windows()
window = sublime.active_window()
view = window.active_view()
view_id = view.id()
window_id = sublime_api.active_window()

window  = sublime.Window(window_id)
view_window = sublime.Window(sublime_api.view_window(view_id))
view    = sublime.View(view_id)

window_active_sheet = sublime_api.window_active_sheet(window_id)
view_sheet_id = sublime_api.view_sheet_id(view_id)
sheet_ids = sublime_api.window_sheets(window_id)
sheets = [sublime.make_sheet(x) for x in sheet_ids]
sheet_window = sublime.make_sheet(view_sheet_id).window()

title = "New HTML Sheet"
sheet_id = sublime_api.window_new_html_sheet(window_id, title, f"<h1>{title}</h1>", 1, 1)
Substitute = (f"""
    <h2>🚩Window & View & Sheet APIs</h2>
    <hr />
    <p>active_window = {window}, active_window_id = {window_id},
    <p>windows = {windows}, view_window = {view_window}, sheet_window = {sheet_window}
    <p>active_view = {view},     active_view_id = {view_id},
    <p>window_active_sheet = {window_active_sheet}
    <p>view_sheet_id = {view_sheet_id}
    <p>sheet_ids = {sheet_ids}
    <p>sheets = {sheets}
    <p>html sheet_id = {sheet_id}"
    """)
sublime_api.html_sheet_set_contents(sheet_id, Substitute)
```


### ===🗝 settings api

配置文件读写管理 API：

```py
import sublime

# Settings API
pc_settings_filename = 'Package Control.sublime-settings'
settings = sublime.load_settings(pc_settings_filename)
settings_to_dict=settings.to_dict()
name_map = settings.get('package_name_map', {})
installed_packages = settings.get('installed_packages')

print(f"""
    {pc_settings_filename}:
    name_map={name_map},
    repositories = {settings.get('repositories')}
    channels = {settings.get('channels')}
    package_name_map = {settings.get('package_name_map', {})}
    installed_packages = {installed_packages}
    package_profiles = {settings.get('package_profiles')}
    debug = {settings.get('debug')}
    submit_usage = {settings.get('submit_usage')}
    platform = {settings.get('platform')}
    version = {settings.get('version')}
    submit_url = {settings.get('submit_url')}
    """)
```

### ===🗝 Prints to panel

直接通过 Sublime API 实现一个 Prints to panel 动态输出文件内容的脚本功能：

```py
import sublime

def print_to_panel(output):
    """
    Prints to panel.
    👉 Sublime Text 4/Package Control/package_control/package_manager.py
    """
    window = sublime.active_window()

    views = window.views()
    view = None
    panel_name = 'Print To Panel.md'
    for _view in views:
        if _view.name() == panel_name:
            view = _view
            break

    if not view:
        view = window.new_file()
        view.set_name(panel_name)
        view.set_scratch(True) # without prompting to save
        view.settings().set("word_wrap", True)
        view.settings().set("auto_indent", False)
        view.settings().set("tab_width", 2)
        view.settings().set("syntax", "Markdown.sublime-syntax")
    else:
        view.set_read_only(False)
        if window.active_view() != view:
            window.focus_view(view)

    def write(string):
        view.run_command('insert', {'characters': string})

    old_sel = list(view.sel())
    old_vpos = view.viewport_position()

    size = view.size()
    view.sel().clear()
    view.sel().add(sublime.Region(size, size))

    if not view.size():
        write((u'''
# Print To Panel
========================

This orginal function code come from Package Control of Sublime Text.
'''))
    write(output)

    # Move caret to the new end of the file if it was previously
    if sublime.Region(size, size) == old_sel[-1]:
        old_sel[-1] = sublime.Region(view.size(), view.size())

    view.sel().clear()
    for reg in old_sel:
        view.sel().add(reg)

    view.set_viewport_position(old_vpos, False)
    # view.set_read_only(True)


def period_update(seconds:int, content: str):
    sublime.set_timeout((lambda it: lambda: print_to_panel(it))(content), seconds*1000)

period_update(0.2, f"""
# ⚡ Introduction

Content generated by a Python Lambda expression, in twice to make a closure to manager free variables.

And update view contents by a sublime.set_timeout API aka:

➡ sublime_api.set_timeout(f, timeout_ms) or 
➡ sublime_api.set_timeout_async(f, timeout_ms)
""")

pc_settings_filename = 'Package Control.sublime-settings'
settings = sublime.load_settings(pc_settings_filename)
installed_packages = settings.get('installed_packages')
period_update(2, f"""\n# ⚡ Installed Packages\n""")
for it in range(1, len(installed_packages)):
    pak = installed_packages[it]
    period_update(it/50 + 2, f"""## ✅ {it} - {installed_packages[it]} \n""")
```


### ===🗝 Output Panels & run_command

Output Panel 也是 View 的一种形式，Sublime 默认提供了 Build Result，对应名称为 output.exec，这个前缀表明了这是一个输出视图对象。可以通过菜单打开：Tools -> Build Results，也可以通过左正角的图标引出 Output Panel 切换菜单。

可以往 Context 菜单添加相应的菜单项，以方便用户打开输出框。

自定义的 Output Panel 的命名也会自动使用 output 前缀，在使用命令打开面板时需要添加这个前缀，注意，使用 window_find_output_panel 查找时不用指定前缀。

window_panels 可以检索所有面板，console 作为默认的控制台输出面板，比较特殊的，还有查找、替换面板，不能通过 window_find_output_panel 查找，不能执行 inser 这些命令。

    ['console', 'find', 'find_in_files', 'output.SFTP', 'output.find_results', 'replace'] 

用户自定义面板都有 output 前缀，它们可以执行命令插入内容。每插入一行内容，都会在当前光标位置进行缩进，需要设置缩进模式及控制光标选区。

Python 标准输出文件在 Sublime 模块中定义为 LogWriter，它会向控制台的缓冲区写入输出数据：

```py
class _LogWriter(io.TextIOBase):
    def __init__(self):
        self.buf = None

    def flush(self):
        b = self.buf
        self.buf = None
        if b is not None and len(b):
            sublime_api.log_message(b)

    def write(self, s):
        if self.buf is None:
            self.buf = s
        else:
            self.buf += s
        if '\n' in s or '\r' in s:
            self.flush()

sys.stdout = _LogWriter()
sys.stderr = _LogWriter()
```

通过改写逻辑，就可以插件的控制台输出重定向到自定义面板。但是对多行文本无效，变通一下使用转义字符解决。

另外，不同类型的命令，需要相应的执行对象，比如，show_panel 命令一般由 window_run_command 执行，使用 view_run_command 就无法打开 *find_in_files* 面板，属于无效命令。

目前 Sublime 集成的 Python 3.8 版本，像 *match* 这种新版本语法是不支持的，使用它会导致无效语法报错。

```py
import sys
import io
from datetime import date, datetime
import sublime_api as sapi
from sublime import *
from sublime_plugin import *

# Console Panel redirect
class _LogWriter(sublime._LogWriter):

    def write(self, s):
        super().write(s)
        if '\n' in s or '\r' in s:
            return sapi.status_message("⚠ console output flush")

        window_id = sapi.active_window()
        unlisted = True
        name = "TestPlugin_OutputPanel"
        panel_id = sapi.window_find_output_panel(window_id, name)
        panel_view = View(panel_id) if panel_id else \
            View(sapi.window_create_output_panel(window_id, name, unlisted))

        panel_view.settings().set("auto_indent", False)
        panel_view.sel().clear()
        panel_view.sel().add(Region(0))

        timestamp = datetime.today().strftime("%H:%M::%S")
        console_output = s.replace("/n/n", "\n")
        panel_view.run_command('insert', {'characters':f'''
--===== 👉TestPlugin Output Panel {panel_view}👈 =====---
=================== {timestamp} ===================
{console_output}
'''})

sys.stdout = _LogWriter()
# sys.stderr = _LogWriter()


# Output Panel API
window_id = sapi.active_window()
window = Window(window_id)
view = View(sapi.window_active_view(window_id))

panels = sapi.window_panels(window_id)
view_ids = sapi.window_views(window_id, True)
# sapi.window_focus_view(window_id, view_id)
views = [{ 
    "view": View(x), 
    "file": View(x).file_name().replace("\\","/").rsplit("/", 1)[1] \
         if View(x).file_name() else "NONAME"
    } for x in view_ids]

name = "TestPlugin_OutputPanel"
panel_id = sapi.window_find_output_panel(window_id, name)
panel = View(panel_id) if panel_id else None
panel.set_name(name)

edit_token = 991
edit = None
try:
    edit = panel.begin_edit(edit_token, "insert", "ABC")
finally:
    panel.end_edit(edit)

print(f'''\
#==> sys.stdout: {sys.stdout}
#==> sys.stderr: {sys.stderr}
#==> sys.stdin: {sys.stdin}
#==> panel name: {panel.name()}
#==> panel id: {panel_id} {panel_id or ": 0 means not a valid id."}
#==> panel view: {panel} {panel or ": Can't find panel view."}
#==> edit: {edit}
#==> is_valid: {panel.is_valid()}
#==> is_in_edit: {panel.is_in_edit()}
#==> is_read_only: {panel.is_read_only()}
#==> is_scratch: {panel.is_scratch()}
#==> panel names: {panels} 
#==> view ids: {view_ids} 
#==> view names: {views} 
'''.replace("\n", "/n/n"))

# Run Command API
cmd = "type_pad"
args =  {"type":"SimpleInputHandler", "text": "Run from TestPlugin.py"}
# view.run_command(cmd, args)
# view.run_command('insert', {'characters': "string"})
# sapi.view_run_command(view_id, cmd, args)
# sapi.window_run_command(window_id, cmd, args)

cmd = "show_panel"
args =  {"panel": "find_in_files"}
args =  {"panel":"output.exec"}      # Build tools output panel
args =  {"panel":"console", "toggle": True}
args =  {"panel":"output.%s" % name} # Other output panel
sapi.window_run_command(window_id, cmd, args)
# sapi.view_run_command(view_id, cmd, args)
```


### ===🗝 Dialogs test

以下脚本可以测试 Sublime 提供的各种 Dialogs，包括输入框等：

```py
import sys
import sublime
import sublime_api

def on_select(*args): show_callback_result("on_select", *args)
def on_done(*args): 
    show_quick_panel(["You have type:", *args], on_select, 1, 0)
    show_callback_result("on_done", *args)
def on_change(*args): show_callback_result("on_change", *args)
def on_cancel(*args): show_callback_result("on_cancel", *args)
def on_highlight(*args): show_callback_result("on_highlight", *args)
def show_callback_result(type, args):
    print(f'''
    show_callback_result:
        type: {type}
        args = {args}
        ''')
    sublime.status_message("⚡show_callback_result: %s -> %s" % (type, str(args)))

def show_input_panel(caption, initial_text, on_done, on_change, on_cancel):
    """ on_done and on_change should accept a string argument, on_cancel should have no arguments """
    window_id = sublime_api.active_window()
    return sublime.View(sublime_api.window_show_input_panel(
        window_id, caption, initial_text, on_done, on_change, on_cancel))

def show_quick_panel(items, on_select, selected_index=-1, flags = None, on_highlight=None, placeholder=None):
    windows = sublime.windows()
    window_id = sublime_api.active_window()
    window  = sublime.Window(window_id)
    view_id = sublime_api.window_active_view(window_id)
    view    = sublime.View(view_id)

    if flags==None and int(sublime.version()) >= 3070:
        flags = sublime.KEEP_OPEN_ON_FOCUS_LOST
    elif flags==None:
        flags = 0

    sublime_api.window_show_quick_panel(
        window_id, items, on_select, on_highlight,
        flags, selected_index, placeholder or '')

# Quick List/Input Panel API
def switchable_panels(index:int = 0):
    selected_index = 1
    flags = 0
    items = [
        "Exit TestPlugin List", 
        "show_quick_panel", 
        "show_input_panel", 
        "window.show_quick_panel", 
        "sublime_api.window_show_quick_panel",
        "sublime_api.window_show_input_panel"]

    window_id = sublime_api.active_window()
    window = sublime.Window(window_id)

    on_select(index)

    item = items[index]

    # match case: # python 3.10
    item == "show_quick_panel" and \
        show_quick_panel(items, switchable_panels, selected_index, flags, on_highlight, items[index])
    item == "show_input_panel" and \
        show_input_panel("TestPlugin", "type some text: show_quick_panel", on_done, on_change, on_cancel)
    item == "window.show_quick_panel" and \
        window.show_quick_panel(items, switchable_panels, selected_index, flags, on_highlight, items[index])
    item == "sublime_api.window_show_quick_panel" and \
        sublime_api.window_show_quick_panel(
                window_id, items, switchable_panels, on_highlight,
                flags, selected_index, 'This is window_show_quick_panel')
    item == "sublime_api.window_show_input_panel" and \
        sublime_api.window_show_input_panel(
            window_id, items[0], items[index], on_done, on_change, on_cancel)
    index == 0 and on_select(index)
    sublime.status_message(f"👉 {item}")
    return items
    
items = switchable_panels()
show_quick_panel(items, switchable_panels, 0)
```


### ===🗝 sublime_api Module

Informations of class or instance: <module 'sublime_api' (built-in)>

<class 'builtin_function_or_method'> Type of: <class 'module'>

    | active_window                | view_classify                             | view_settings                          |
    | architecture                 | view_clear_undo_stack                     | view_sheet_id                          |
    | buffer_add_text_listener     | view_clones                               | view_show_point                        |
    | buffer_clear_text_listener   | view_command_history                      | view_show_point_at_center              |
    | buffer_file_name             | view_context_backtrace                    | view_show_popup                        |
    | buffer_primary_view          | view_element                              | view_show_popup_table                  |
    | buffer_views                 | view_em_width                             | view_show_region                       |
    | buffers                      | view_encoding                             | view_show_region_at_center             |
    | cache_path                   | view_end_edit                             | view_size                              |
    | can_accept_input             | view_erase                                | view_split_by_newlines                 |
    | channel                      | view_erase_phantom                        | view_style                             |
    | decode_value                 | view_erase_phantoms                       | view_style_for_scope                   |
    | encode_value                 | view_erase_regions                        | view_substr                            |
    | error_message                | view_erase_status                         | view_symbol_regions                    |
    | executable_path              | view_expand_by_class                      | view_symbols                           |
    | expand_variables             | view_export_to_html                       | view_text_point                        |
    | find_resources               | view_extract_completions                  | view_text_point_utf16                  |
    | find_syntax_for_file         | view_extract_scope                        | view_text_point_utf8                   |
    | gather_plugin_profiling_data | view_extract_tokens_with_scopes           | view_text_to_layout                    |
    | get_clipboard                | view_file_name                            | view_transform_region_from             |
    | get_clipboard_async          | view_find                                 | view_unfold_region                     |
    | get_log_build_systems        | view_find_all                             | view_unfold_regions                    |
    | get_log_commands             | view_find_all_results                     | view_update_popup_content              |
    | get_log_control_tree         | view_find_all_results_with_text           | view_viewport_extents                  |
    | get_log_fps                  | view_find_all_with_contents               | view_viewport_position                 |
    | get_log_indexing             | view_find_by_class                        | view_visible_region                    |
    | get_log_input                | view_find_by_selector                     | view_window                            |
    | get_log_result_regex         | view_fold_region                          | view_window_to_layout                  |
    | get_macro                    | view_fold_regions                         | view_word_from_point                   |
    | get_syntax                   | view_folded_regions                       | view_word_from_region                  |
    | html_sheet_set_contents      | view_full_line_from_point                 | window_active_group                    |
    | incompatible_syntax_patterns | view_full_line_from_region                | window_active_panel                    |
    | installed_packages_path      | view_get_name                             | window_active_sheet                    |
    | list_syntaxes                | view_get_overwrite_status                 | window_active_sheet_in_group           |
    | load_binary_resource         | view_get_regions                          | window_active_view                     |
    | load_resource                | view_get_status                           | window_active_view_in_group            |
    | load_settings                | view_has_non_empty_selection_region       | window_automate_ui                     |
    | log_build_systems            | view_hide_popup                           | window_bring_to_front                  |
    | log_commands                 | view_indentation_level                    | window_can_accept_input                |
    | log_control_tree             | view_indented_region                      | window_close_file                      |
    | log_fps                      | view_indexed_references                   | window_create_output_panel             |
    | log_indexing                 | view_indexed_symbol_regions               | window_destroy_output_panel            |
    | log_input                    | view_indexed_symbols                      | window_extract_variables               |
    | log_message                  | view_insert                               | window_file_history                    |
    | log_result_regex             | view_is_auto_complete_visible             | window_find_open_file                  |
    | message_dialog               | view_is_dirty                             | window_find_output_panel               |
    | notify_application_commands  | view_is_folded                            | window_focus_group                     |
    | ok_cancel_dialog             | view_is_in_edit                           | window_focus_sheet                     |
    | open_dialog                  | view_is_loading                           | window_focus_view                      |
    | packages_path                | view_is_popup_visible                     | window_folders                         |
    | platform                     | view_is_primary                           | window_get_layout                      |
    | plugin_host_loaded_plugins   | view_is_read_only                         | window_get_project_data                |
    | plugin_host_ready            | view_is_scratch                           | window_get_sheet_index                 |
    | profile_syntax_definition    | view_layout_extents                       | window_get_view_index                  |
    | run_command                  | view_layout_to_text                       | window_is_dragging                     |
    | run_syntax_test              | view_layout_to_window                     | window_is_ui_element_visible           |
    | save_dialog                  | view_line_endings                         | window_lookup_references               |
    | save_settings                | view_line_from_point                      | window_lookup_references_in_open_files |
    | score_selector               | view_line_from_region                     | window_lookup_symbol                   |
    | select_folder_dialog         | view_line_height                          | window_lookup_symbol_in_open_files     |
    | set_clipboard                | view_lines                                | window_new_file                        |
    | set_timeout                  | view_match_selector                       | window_new_html_sheet                  |
    | set_timeout_async            | view_meta_info                            | window_num_groups                      |
    | settings_add_on_change       | view_preserve_auto_complete_on_focus_lost | window_open_file                       |
    | settings_clear_on_change     | view_query_phantoms                       | window_panels                          |
    | settings_erase               | view_replace                              | window_project_file_name               |
    | settings_get                 | view_reset_reference_document             | window_run_command                     |
    | settings_get_default         | view_retarget                             | window_select_sheets                   |
    | settings_has                 | view_row_col                              | window_selected_sheets                 |
    | settings_set                 | view_row_col_utf16                        | window_selected_sheets_in_group        |
    | settings_to_dict             | view_row_col_utf8                         | window_set_layout                      |
    | sheet_close                  | view_run_command                          | window_set_project_data                |
    | sheet_file_name              | view_scope_name                           | window_set_sheet_index                 |
    | sheet_group                  | view_score_selector                       | window_set_ui_element_visible          |
    | sheet_is_semi_transient      | view_selection_add_point                  | window_set_view_index                  |
    | sheet_is_transient           | view_selection_add_region                 | window_settings                        |
    | sheet_set_name               | view_selection_clear                      | window_sheets                          |
    | sheet_view                   | view_selection_contains                   | window_sheets_in_group                 |
    | sheet_window                 | view_selection_erase                      | window_show_input_panel                |
    | status_message               | view_selection_get                        | window_show_quick_panel                |
    | ui_info                      | view_selection_size                       | window_status_message                  |
    | verify_pc_signature          | view_selection_subtract_region            | window_symbol_locations                |
    | version                      | view_set_completions                      | window_system_handle                   |
    | view_add_phantom             | view_set_encoding                         | window_template_settings               |
    | view_add_regions             | view_set_line_endings                     | window_transient_sheet_in_group        |
    | view_assign_syntax           | view_set_name                             | window_transient_view_in_group         |
    | view_begin_edit              | view_set_overwrite_status                 | window_views                           |
    | view_buffer_id               | view_set_read_only                        | window_views_in_group                  |
    | view_cached_substr           | view_set_reference_document               | window_workspace_file_name             |
    | view_can_accept_input        | view_set_scratch                          | windows                                |
    | view_change_count            | view_set_status                           | yes_no_cancel_dialog                   |
    | view_change_id               | view_set_viewport_position                |                                        |


## ==⚡ LaTeX WebViewer/First Column/Index Rows

Sublime Text 插件开发，以下功能于 Windows 平台 4121 版本正常使用：

- ViewLatexListener 监听事实，提供代码片段输入功能；
- ViewLatexCommand 处理当前选择区的 LaTeX 内容，并调用在线的 Equation Editor 显示数学公式；
- FirstColumnCommand 处理当前选区，将选区处理成为选择所有相关行的第一列，即包最靠近行首、含多个空格或一个 Tab 符号的位置；
- IndexRowsCommand 调用上一个命令插件，并在每行首位置插入一个从 1 开始的数值编号；

Sublime Text 插件开发基础知识点：

- 基于 Python 开发，需要函数式或 OOP 编程相关的编程基础；
- 插件的触发途径：
    - 通过 Python Console 直接使用代码调用，需要掌握 Sublime Python API；
    - 通过菜单触发，需要配置相关的 .sublime-menu 菜单文件；
    - 通过 Command Palette 面板触发，需要配置 .sublime-command 文件；
    - 通过快速键触发，需要配置 .sublime-keyman 文件，通过菜单操作 Preferences -> Key Bindings；
- Sublime Text 主要插件相关 Python API 类型：
    -  sublime 模块，提供版本号、配置信息读写、系统剪贴版、状态栏访问等全局功能，和相应的类型：
        -  sublime.Settings 配置信息类型，包含配置文件类型的增、删等处理功能，通过模块提供的方法读写；
        -  sublime.Options
        -  sublime.Window 窗口类型，Sublime Text 窗口管理了所有视图及编辑的文件；
        -  sublime.View 视图类型，即打开每个文件的并看到内容的 UI 界面所代表的类型；
        -  sublime.Edit 没有提供功能，代表视图对应的一个编辑器标志；
        -  sublime.Region 当前视图对象所有对应的光标选区对象；
        -  sublime.RegionSet 选区集合对象；
        -  sublime.Sheet 是数据容器，可以包含编辑文件的 View 或者图像预览等；
        -  sublime.TextSheet(Sheet) 
        -  sublime.ImageSheet(Sheet) 
        -  sublime.HtmlSheet(Sheet) 
        -  sublime.Html 用于区分 HTML 内容和文本，数据保存在 data 属性； 
        -  sublime.Phantom
        -  sublime.PhantomSet
    -  sublime_plugin 插件模块，没有提供方法功能，只包含不同插件类型依赖的接口类型：
        -  sublime_plugin.EventListener 事件监听处理类型；
        -  sublime_plugin.ViewEventListener 视图事件处理；
        -  sublime_plugin.TextChangeListener 文本改动事件处理；
        -  sublime_plugin.Command 插件基础类，早期文档使用 Plugin；
        -  sublime_plugin.ApplicationCommand(Commnd) 应用类型插件；
        -  sublime_plugin.WindowCommand(Commnd) 窗口交互类型插件，每个窗口只实例化一次/个插件，self.window 引用窗口；
        -  sublime_plugin.TextCommand(Commnd) 文本处理类型插件，self.view 引用视图，并在构造函数中保存引用；
        -  sublime_plugin.CommandInputHandler 用户输入处理处理器类型实现；
        -  sublime_plugin.BackInputHandler(CommandInputHandler) 基本输入处理类型结构，需要实现更多多的接口方法；
        -  sublime_plugin.TextInputHandler(CommandInputHandler) 文本输入处理；
        -  sublime_plugin.ListInputHandler(CommandInputHandler) 为输入提供后选内容列表；

继承命令对象，最主要的是处理以下四个方法：

- ↪`run(<args>)` -> None: 执行插件命令时调用；
- ↪`is_enabled(<args>)` -> bool: 在准备阶段调用，给插件开发者提供一个时机，以确定插件功能是否可供用户使用。
- ↪`is_visible(<args>)` -> bool: 在准备阶段调用，给插件开发者一个时机，以设置插件菜单等是否可被用户看见。
- ↪`description(<args>)` -> String: 插件设置了菜单时，加载插件后并要确定菜单栏显示的标题时调用。

Sublime Text 插件加载机制可以参数安装目录下的脚本源代码，如：Sublime Text 3\Lib\python38\sublime_plugin.py 和 sublime.py，在内部，使用了非开源的 Plugin Host 导出的 sublime_api 接口。

插件模块中 *all_callbacks* 定义了 53 个类型类型，这么多主要是有 19 个 async 版本的事件：

- 继承 *EventListener* 可以响应处理所有这事件。
- 继承 *ViewEventListener* 专注处理视图事件，不能处理 *view_event_listener_excluded_callbacks* 指定的 25 个不太相关的事件。
- 继承 *TextChangeListener* 只处理 *text_change_listener_callbacks* 指定的 6 个事件，on_text_changed、on_revert、on_reload，以及它们的异步版本。

主要是 *ViewEventListener* 视图事件，列表如下，18 个，外加异步版本 10 个：

|       View Events       |         Async Version         |
|-------------------------|-------------------------------|
| [on_activated]          | [on_activated_async]          |
| [on_close]              | -                             |
| [on_deactivated]        | [on_deactivated_async]        |
| [on_hover]              | -                             |
| [on_load]               | [on_load_async]               |
| [on_modified]           | [on_modified_async]           |
| [on_post_move]          | [on_post_move_async]          |
| [on_post_save]          | [on_post_save_async]          |
| [on_post_text_command]  | -                             |
| [on_pre_close]          | -                             |
| [on_pre_move]           | -                             |
| [on_pre_save]           | [on_pre_save_async]           |
| [on_query_completions]  | -                             |
| [on_query_context]      | -                             |
| [on_reload]             | [on_reload_async]             |
| [on_revert]             | [on_revert_async]             |
| [on_selection_modified] | [on_selection_modified_async] |
| [on_text_command]       | -                             |

在文本处理插件开发中，选区、和选区集合是非常重要的类型。Region 对象代表一个选择区间，包含 a 和 b 两个属性，begin 和 end 方法，它们指定了这个选区起止字符位置。注意，根据鼠标或键盘控制选择方向的不同，a b 值的大小也不同，向下选择时 a > b。 dir 函数并不能获取到 Region 的属性列表内容，使用 print 函数可以打印这两个值出来。

Selection 即 RegionSet 对象包含多个选区对象，View.sel() 方法获取当的选区集合。

自定义右键菜单，就创建自己的 Context.sublime-menu 等菜单配置文件，默认的右键菜单配置在 Packages\Default\Context.sublime-menu。

可用的菜单配置文件命名规则如下，名称决定了菜单的类型，注意名称大小写和空格：

- *Main.sublime-menu* 窗口主菜单配置文件；
- *Context.sublime-menu* 文件内容视图右键菜单配置文件；
- *Find in Files.sublime-menu* 查找文件 ... 按键弹出菜单配置文件；
- *Tab Context.sublime-menu* 文件选项卡右键菜单配置文件；
- *Widget Context.sublime-menu* 小工具面板右键菜单配置文件，如命令列表面板中的右键菜单；
- *Side Bar.sublime-menu* 侧栏目录树右键菜单配置文件；
- *Side Bar Mount Point.sublime-menu* 侧栏目录树顶级目录右键菜单配置文件；
- *Encoding.sublime-menu* 状态栏编码选择菜单配置文件；
- *Line Endings.sublime-menu* 状态栏编码选择菜单配置文件；
- *Indentation.sublime-menu* 状态栏缩进选择菜单配置文件；
- *Syntax.sublime-menu* 状态栏文件语法类型选择菜单配置文件；

Side Bar 或者 Side Bar Mount Point 两个菜单的操作会涉及文件、目录，所以需要在配置菜单时设置 args 参数列表，像如下这样配置，使用 *paths* 和 *files* 来传递侧栏目录树操作相关的目录或文件。并且命令类实现 run 方法时，除了 self、view 两个默认要求的参数外，需要相应添加 args 指定的额外参数列表：

```json
[
    {
        "caption": "View Latex",
        "command": "view_latex",
        "mnemonic": "V",
        "id": "view_latex",
        "args": {"paths": [],"files": []}
    }
]
```

多选文件支持，通过实现 *is_enabled* 来决定命令是不否有效，可以参考 SideBarEnhancements 插件的实现。

另外，读取菜单配置文件时注意，因为 JSON 中不是规范的数据，注意最外层的方括号，规范 JSON 最外层是花括号。所以 sublime.load_settings() 不能加载到菜单配置数据，并且 sublime.save_settings() 将规范 JSON 写入会导致菜单配置不正确。可以考虑使用 *load_resource* 加载资源字符串内容进行处理：

```py
# str = sublime.load_resource('Packages/User/Context.sublime-menu')
s = sublime.load_settings('Context.sublime-menu') 
print(s.to_dict())
s.set("caption","ViewLatex")
children = s.get('children') or [{"caption":"empty"}]
print(children[0])
children[0]["caption"] = "Message changed" 
s.set('children', children) 
sublime.save_settings('Context.sublime-menu') 
```

运行命令查看事件响应统计数据 Plugin Development: Profile Events

几条事件触发线路：

- 输入内容时，如果文件有启用提示，或者使用 Tab 触发，并且光标在单词尾，但没有找到合适内容时，就会触发 on_query_completions 事件获取候选内容。
- 改变光标、选择内容时：on_text_command -> on_selection_modified -> on_post_text_command
- 打开现有文件时： on_activated [View(403)] -> on_load [View(403)]-> on_deactivated [View(401)]
- 创建新文件缓冲区时： on_window_command(new_file) -> on_deactivated(old view) -> on_activated(new view) -> on_new
- 关闭文件缓冲区时： on_window_command(close) -> on_pre_close(thisview) -> on_deactivated - on_activated(otherviwe) -> on_close(thisview)

- on_query_context 事件比较多参数，触发时机也比较混乱，具体参考 API 文档。
- on_hover 事件在光标移动时触发，参数有光标所在字符位置，具体参考 API 文档。
- on_query_completions 事件可以很好地通过提供自动完成内容来替代 code sippet 功能。

Key Bindings/Menus/Command 配置参考：

```json
[
    {
        "caption": "View Latex",
        "command": "view_latex",
        "mnemonic": "V",
        "id": "view_latex",
        "keys": ["f1"], 
        "args": {"paths": [],"files": []}
    },
    {
        "caption": "First Column",
        "command": "first_column",
        "mnemonic": "F",
        "id": "first_column",
        "keys": ["alt+m"], 
        "args": {"paths": [],"files": []}
    },
    {
        "caption": "Index Rows",
        "command": "index_rows",
        "mnemonic": "I",
        "id": "index_rows",
        "keys": ["f5"], 
        "args": {"paths": [],"files": []}
    }
]
```

以下是插件代码实现，保存文件 ViewLatex.py 即相应会产生 User.ViewLatex 模块：

```py
import os
from code import InteractiveConsole
import urllib
import sublime
import sublime_plugin

print("Sublime Text version %s"%sublime.version())
# print("View Events:")
# for event in sublime_plugin.all_callbacks.keys():
#   if event not in sublime_plugin.view_event_listener_excluded_callbacks:
#     print("\t[%s]"%event)

def info(cls):
  print("cls.inf() %s"%cls.inf);
  print("cls.info() %s"%cls.info);

# @classmethod 
# from User.ViewLatex import inf
# import sublime, sublime_api, sublime_plugin
# inf(sublime_api)
def inf(cls, obj=None):
  target = obj or cls;
  print("Informations of class or instance: %s\n"%(target))
  for p in dir(target):
    if p.startswith("__"): continue # pass by magic methods
    attr = None
    try:
      attr = "is " + str(type(getattr(target,p)))
    except Exception as e:
      attr = ": " + str(e)
    inf = "%s %s" % (p.rjust(26), attr)
    print(inf)


class ViewLatexListener(sublime_plugin.EventListener):

  # def on_activated(self, view):
  #   print("VLL: on_activated [%s]" % view)

  # def on_close(self, view):
  #   print("VLL: on_close [%s]" % view)

  # def on_deactivated(self, view):
  #   print("VLL: on_deactivated [%s]" % view)

  # def on_hover(self, view, pos, zone):
  #   zones = "T%s G%s M%s" %(sublime.HOVER_TEXT, sublime.HOVER_GUTTER, sublime.HOVER_MARGIN)
  #   print("VLL: on_hover [%s] [pos %s] [zone %s] %s" % (view, pos, zone, zones))

  # def on_load(self, view):
  #   print("VLL: on_load [%s]" % view)

  # def on_modified(self, view):
  #   print("VLL: on_modified [%s] [%s]" % (self,view))
  #   if hasattr(view, 'livePythonInterpreter'):
  #     print('VLL: Modified and interpreting.')
  #   else:
  #     print('VLL: Modified but not interpreting.')

  # def on_new(self, view):
  #   print("VLL: on_new [%s]" % view)

  # def on_post_save(self, view):
  #   print("VLL: on_post_save [%s]" % view)

  # def on_post_text_command(self, view, act, extras):
  #   act in ['move','drag_select','left_delete','right_delete','redo_or_repeat','find_next'] #....
  #   print("VLL: on_post_text_command [%s] [act %s] %s" % (view, act, extras))

  # def on_pre_close(self, view):
  #   print("VLL: on_pre_close [%s]" % view)

  # def on_pre_save(self, view):
  #   print("VLL: on_pre_save [%s]" % view)

  def on_query_completions(self, view, prefix, locations):
    print("VLL: on_query_completions [%s] [%s] [%s]" % (view, prefix, locations))
    return [] or [
      ("prefix", "description", "prefix => value"),
      ("code",   "Code block", "```${1:syntax}\n${2:codes}\n```"),
      ("matlab", "Matlab code block", "```${1:matlab}\n${2:codes}\n```"),
      ("py",     "Python code block", "```${1:py}\n${2:codes}\n```"),
      ("cpp",    "cpp code block", "```${1:cpp}\n${2:codes}\n```"),
      ("cs",     "cs code block", "```${1:cs}\n${2:codes}\n```"),
      ("xml",    "xml code block", "```${1:xml}\n${2:codes}\n```"),
      ("json",   "json code block", "```${1:json}\n${2:codes}\n```"),
      ]

  # def on_query_context(self, view, key, op, opr, match_all):
  #   print("VLL: on_query_context [%s] [%s] [%s] [%s] [%s]" % (view, key, op, opr, match_all))       

  # def on_selection_modified(self, view):
  #   print("VLL: on_selection_modified [%s]" % view)

  # def on_text_command(self, view, act, extras):
  #   act in ['move','drag_select','left_delete','right_delete','redo_or_repeat','find_next'] #....
  #   print("VLL: on_text_command [%s] [act %s] %s" % (view, act, extras))

  # def on_window_command(self, view, act, b):
  #   act in ['new_file', 'close']
  #   print("VLL: on_window_command [%s] [act %s] [%s]" % (view, act, b))


class ViewLatexCommand(sublime_plugin.TextCommand):
  def __init__(self, view):
    self.view = view
    print("VLC ViewLatexCommandview init %s %s\n%s\n" 
      %(view, __name__, __file__))

    if hasattr(view, 'livePythonInterpreter'):
        print('VLC: Already had an interpreter, but replacing it.')
    else:
        print("VLC: Didn't have an interpreter, making one now.")
    view.livePythonInterpreter = InteractiveConsole()

  def run(self, edit, files, paths):
    # print([edit,files,paths])
    print(self.view.file_name())
    # print(self.view.sel())
    # self.info()

    # print({"view.settings()":self.view.settings().to_dict()})
    # s = sublime.load_settings('Packages/User/Context.sublime-menu') 
    # print(s)
    # s.set("caption","ViewLatex")
    # children = s.get('children') or [{"caption":"empty"}]
    # print(children[0])
    # children[0]["caption"] = "Message changed" 
    # s.set('children', children) 
    # sublime.save_settings('Context.sublime-menu') 

    for region in self.view.sel():

      current = self.view.full_line(region.begin()) # region of current line with NEWLINE
      current = self.view.line(region.begin()) # region of current line
      linetxt = self.view.substr(current);
      select = self.view.substr(region);
      content = self.view.substr(sublime.Region(0, 15))
      latex = linetxt;

      if(region.a == region.b):
        print("ViewLatex: select nothing %s" % region)
      else:
        latex = select
        # self.view.replace(edit, region, "%i %s" %(i, txt))
      '''
      F(t) = A_0/2 + \sum_{n=1}^{\infty} A_n cos(n\omega_0 t) + B_n sin(n\omega_0 t)
      '''
      startweb = "start https://latex.codecogs.com/svg.latex?%s" % urllib.parse.quote(latex.strip())
      # os.system(startweb)
      os.startfile(startweb.replace("start ",""))

      # print({
      #   "Line Text":linetxt,
      #   "Selected Text": select,
      #   "startweb": startweb,
      #   "line(25)": 
      #           self.view.line(25), # region of line at position 25
      #   "full_line(25)": 
      #           self.view.full_line(25), # region of line at 25, LineEndings included
      #   "line(Region(1, 50))": 
      #           self.view.line(sublime.Region(1, 50)), # region spans lines at position 1 to 50
      #   "full_line(Region(1, 50))": 
      #           self.view.full_line(sublime.Region(1, 50)), # region spans lines at postion 1 to 50, with LineEndings
      #   "lines(Region(1,32))": 
      #           self.view.lines(sublime.Region(1,32)), # region of all lines between [1, 32]
      #   "word(15)": 
      #           self.view.word(15), # region of wold at position 15
      #   },"\n")

      # self.view.sel().clear() # unselect
      # self.view.sel().add(sublime.Region(20, 40))
      # self.view.show(self.view.size()) # set view position to end

      # sublime.set_clipboard('ViewLatexCommand') # set system clipboard
      # self.view.erase(edit, Region(0, self.view.size())) # clear content
      # self.view.insert(edit, 0, "#Hello, World!\n") # insert text at very first
      # self.view.replace(edit, current, "NEW LINE CONTENT!")
      
      # print(self.view.line_height()) # font-size line-height
      # print(self.view.line_endings()) # status bar LineEndings setting

class FirstColumnCommand(sublime_plugin.TextCommand):
  def __init__(self, view):
    self.view = view
    print("FCC FirstColumnCommand init [%s] [%s]...\n%s\n"%(self, view, __file__))
  def run(self, edit, paths, files):
    # ViewLatexCommand.inf(edit) # Print Edit API Information
    # ViewLatexCommand.inf(self.view) # Print View API Information
    # ViewLatexCommand.inf(self.view.sel()) # Print RegionSet API Information
    print("FirstColumnCommand...")
    selections = self.view.sel()
    lines = []
    for region in selections:
      lines = lines + self.view.lines(region)

    self.view.sel().clear()
    # self.view.sel().add_all(lines)
    for line in lines:
      c1 = self.view.find(r"\t|\s\s+", line.a)
      if(c1.b>line.b) : c1 = sublime.Region(line.a,line.a)
      self.view.sel().add(c1)

class IndexRowsCommand(sublime_plugin.TextCommand):
  def __init__(self, view):
    self.view = view
    print("IRC init [%s] [%s]...\n%s\n"%(self, view, __file__))

  def run(self, edit, paths, files):
    view = self.view
    print(["IRC run ", view.sel()])
    # FirstColumnCommand(view).run(edit, [], [])

    regionset = view.sel()

    nums = []
    alllines = []
    for region in regionset:
      index = 0
      lines = view.lines(region)
      alllines+=(lines) # list extend
      for region in lines:
        index += 1
        nums.append(index)

    # print(alllines)
    view.sel().clear()
    # for region in regionset:
      # view.sel().subtract(region)

    index = 0
    view.sel().add_all(alllines)
    for region in view.sel():
      view.insert(edit, region.a, str(nums[index]))
      index += 1

  # def description(self, *args, **kwargs):
  def is_enabled(self, *args, **kwargs):
    regionset = self.view.sel()
    print("is_enabled(self, *args): %s %s" % (args, kwargs))
    # print(regionset)
    return len(regionset)>0 and len(regionset)>1 or regionset[0].b != regionset[0].a 
```


## ==⚡ Input handlers 用户输入处理
- https://docs.sublimetext.io/guide/extensibility/plugins/input_handlers.html

Input handlers are a mechanism to query a user for one or multiple input parameters via the Command Palette. They replace the older method of input and quick panels (Window.show_input_panel and Window.show_quick_panel) for a unified user experience in a single component.

Input Handlers have been added in build 3154 and were first available on the stable channel in version 3.1.

➡ **Examples**
The following commands provided by Sublime Text's Default package use input handlers (command names are for the Command Palette):

|    Command name   |          File         |                        Description                        |
|-------------------|-----------------------|-----------------------------------------------------------|
| Arithmetic        | Default/arithmetic.py | Evaluates a given expression.                             |
| View Package File | Default/ui.py         | Provides a list of all resource files.                    |
| Rename File       | Default/rename.py     | Queries the user for a new file name for the active view. |

You can use the above View Package File command to view the source code of these files.

➡ **Input Handler Kinds**
There are currently two types of input handlers:

- text input handlers accepting arbitrary text input,
- list input handlers providing a list of options for the user to choose from.

Text input handlers always forward the entered text to the command, while list input handlers can handle any JSON-serializable value, accompanied by a caption for their respective list entry.

典型的用户输入处理是 Command Palette 中提供并接收用户输入的数据，需要插件 run 函数中设置相应的参数接收。调用插件时，Sublime Text 通过插件的 input 方法的实现来检查插件是否需要处理用户数据输入。如果返回一个输入处理器接口类型，那么就会有用户输入的交互流程。而具体的数据处理就通过插件开发者实现输入处理逻辑，也就是 *CommandInputHandler* 接口类型的具体实现。

基本的程序逻辑如下：

- 通过命令面板加载插件后，先调用 input_description(self) 获取用户输入状态下展示的提示性内容；
- 在插件基础类 *Command* 内部有通过 create_input_handler_ 函数调用 input(self, args) 以检查是否实现了数据输入处理逻辑；
- 插件返回一个输入处理器接口类型 *CommandInputHandler* 实例，并在其中实现数据交互输入的处理。

输入处理器接口类型运行流程：

- 插件方法 *input* 返回一个输入处理器后，进入用户输入交互流程；
- 进入准备阶段，内部方法 *setup_* 依次调用以下初始化方法：
    - *name(self)* 默认返回类名，下划线分隔大写字母，不包括 input_handler 后缀，用来确认插件 run 方法接收字符串的参数名。
    - *initial_text(self) -> str* 需要返回一个字符串，作为输入框的默认值；
    - *initial_selection(self)* 这是一个通知性调用，插件开发者可以在这里做一些关于文件选区的处理；
    - *placeholder(self)* 
- 如果用户按 ESC 取消输入，就会触发 *cancel* 方法，并结束本轮流程；
- 如果用户输入内容，则持续触发预览 *preview(self, text)*，需要返回字符串或 sublime.Html 内容，以显示到输入面板；
- 如果用户按下回车，就会调用 *validate(self, text) -> bool* 验证用户输入是否有效；
- 通过验证后，Sublime 会调用 *confirm(self, text) -> None* 通知插件输入已经通过验证，下一步准入将内容插入视图；
- 插件主方法 *run(self, edit, text)* 正式执行，并会接收到传入的用户数据，这里可以再进一步对数据进行处理，并调用视图提供的方法修改文件内容；

通过 *want_event() -> bool* 方法返回值可以控制验证、确认函数是否需要使用 event 参数：

- self.validate(v, event)
- self.confirm(v, event)

参数 event 包含控制组合键的状态信息，如：

- 只按下 Alt： {'modifier_keys': {'alt': True}}
- 只按下 Shift： {'modifier_keys': {'shift': True}}
- 只按下 Ctrl： {'modifier_keys': {'ctrl': True, 'primary': True}}
- 同时按下 Ctrl+Alt+Shift：{'modifier_keys': {'alt': True, 'ctrl': True, 'primary': True, 'shift': True}}

输入处理插件接口 *CommandInputHandler* 有三种：

- BackInputHandler(CommandInputHandler): 只定义了 name(self) 方法，返回 "_Back"；
- TextInputHandler(CommandInputHandler): 基本字符串输入实现，定义了内部的配置方法；
- ListInputHandler(CommandInputHandler): 带候选内容列表的输入实现，定义了内部的配置方法；

一般文本输入实现与列表候选输入实现的差别在于内部配置方法的配置 setup_(self, args)，以下是这两种配置的对比：

        props = {
            "initial_text": self.initial_text(),
            "initial_selection": self.initial_selection(),
            "placeholder_text": self.placeholder(),
            "type": "text",
        }

        props = {
            "initial_text": self.initial_text(),
            "placeholder_text": self.placeholder(),
            "selected": selected_item_index,
            "type": "list",
        }

可以看到异同点在于：

- 文本输入有 *initial_selection* 而列表输入没有；
- 列表输入有 *selected_item_index* 可以指定默认候选内容的序号；
- 文本输入、列表输入指定 type 值分别为 *text* 和 *list*; 
- 它们都有 *initial_text* 设置初始值和占位符内容 *placeholder_text*，它会以浅色调显示在输入面板的背景中；

列表指定默认候选内容的序号时，不是通过专用函数，而是通过 *list_items* 返回值类型来设置，并且必需实现此方法否则插件不能正确运行：

- 返回 tuple 为 (items, index) 即可以指定默认序号为: index
- 返回 list 为 [items...] 就不设置默认序号： selected_item_index = -1


关于 *name()* 这个函数的返回值，里面有个 Python 编程上的问题，是关于可变长函数参数列表处理的问题。

Python 采用可命名参数的函数调用方式，即调用函数时，可以使用参数名来指定要传递的数据。

可变长参数传递的两种方式、两种数据类型：

- `*args` 列表传递，用在函数参数列表以接收任意数量的非命名参数，用在调用函数时将 *tuple* 扩展开来；
- `*kwargs` 字典传递，用在函数参数列表以接收任意数量的命名参数，用在调用函数时将 *dict* 扩展开来；

可变长参数函数方法中，`*args` 用来将参数打包成 tuple 给函数体调用，`**kwargs` 打包关键字参数成 dict 给函数体调用，这是 Python 特有的语法结构。

定义函数时，参数列表必需按：非命名参数、`*args`、命名参数和、`**kwargs` 这样的位置必须保持以下这种顺序，不能打乱，可以省略不传，但参形式不能乱放。args 或 kwargs 这个名字不重要，重点是星号的数量。

Sublime Text 调用插件主方法时，使用的是以下这种方式：

    self.run(edit, **args)

这就表示编写插件时，插件命令、菜单项、快捷键输入的参数，即 *args* 字段内中配置的参数名称必需和 run 函数参数列表统一，或者是使用 `def run(self, edit, *args, **kwargs)` 这种省事的形式，这样无论传递什么参数都可以接收到。

参数列表和传入参数的命名不统一时，就会出现类似以下这样的错误：

    >>> window.run_command("type_pad")
    Traceback (most recent call last):
      File "C:\Program Files\Sublime Text 3\Lib\python38\sublime_plugin.py", line 1518, in run_
        return self.run(edit)
    TypeError: run() missing 1 required positional argument: 'text'

应该在参数中加入 *args* 配置数据，或者按上面说明的方式，修改函数参数列表：

    >>> window.run_command("type_pad",{"text":"abc"})
    abc

了解这此后，就可以在 *input* 方法中依次创建多个输入处理器，供用户输入多个参数，并且完全输入后，参数再汇总传入 *run* 函数。因为，多个输入处理器就需要多个命名参数对应接收处理，构造 *CommandInputHandler* 实例时，可以记录一个参数名，并且通过 *name()* 函数返回给插件加载程序使用。


在使用多个输入处理器的情况下，*next_input* 函数就起作用了，通过它可以让用户连续输入多组数据。

```py
class MultiNumberInputHandler(sublime_plugin.TextInputHandler):
def __init__(self, names):
    self._name, *self.next_names = names

def name(self):
    return self._name

def placeholder(self):
    return "Number"

def next_input(self, args):
    if self.next_names:
        return MultiNumberInputHandler(self.next_names)
```

插件命令配置参考如下，需要写入配置文件 Default.sublime-commands：

```json
[
    { "caption": "Type Pad [Multiple]", "command": "type_pad", "args": {"type":"MultipleInputHandler" }},
    { "caption": "Type Pad [SimpleList]", "command": "type_pad", "args": {"type":"SimpleListInputHandler" }},
    { "caption": "Type Pad [Simple]", "command": "type_pad", "args": {"type":"SimpleInputHandler", "text":"✒TEST TYPEPAD"}},
    { "caption": "Type Pad [Any]", "command": "type_pad", "args": {"type":"AnyInputHandler"}},

]
```

TypePad 插件示范代码如下，包含 SimpleInputHandler、SimpleListInputHandler、MultipleInputHandler 三种形式，都统一通过 TypePadCommand 插件命令调用，如果分开处理会更简洁：

```py
import sublime
import sublime_plugin
import sublime_api
from User import TypePad

# Run in Python Console
# view.run_command("type_pad",{"text":""})
# window.run_command("type_pad",{"text":""})
class TypePadCommand(sublime_plugin.TextCommand):

    ops = ['operand1', 'operand2']

    def run(self, edit, **kwargs):
        ops = self.ops
        litxt = kwargs['simple_list'] if 'simple_list' in kwargs else ""
        litxt = "&"+litxt if litxt and litxt.endswith(";") else litxt
        op1 = kwargs[ops[0]] if ops[0] in kwargs else "";
        op2 = kwargs[ops[1]] if ops[1] in kwargs else "";
        text = kwargs['text'] if 'text' in kwargs else ""

        if len(kwargs.keys()) == 1:
            return
        text = text or litxt or ""
        bothFloat = checkNumber(op1) and checkNumber(op1)
        text = str(float(op1) * float(op2)) if bothFloat else text
        print("TypePad run(): text: %s kwargs: %s" % (text, kwargs))
        for region in self.view.sel():
            self.view.replace(edit, region, text)

    def input_description(self): # return a text show on left of input box in GUI
        return "Type Here:"

    def input(self, args):
        typeid = args["type"] if "type" in args else "" 
        names = [name for name in self.ops if name not in args]
        print("TypePad input() args: %s names: %s" % (args, names))
        if not hasattr(TypePad, typeid):
            sublime.status_message("TypePad incorrect type: 👉 %s" % typeid)
            return None
        Type = getattr(TypePad, typeid)
        parameters = dict(
            MultipleInputHandler = dict(view=self.view, names=names),
            SimpleListInputHandler = dict(),
            SimpleInputHandler = dict(view=self.view),
            )
        if typeid in parameters:
            return Type(**parameters[typeid])
        else:
            sublime.status_message("TypePad needs: 👉 Multiple, SimpleList or Simple InputHandler")
        return None

    def on_select(self, args):
        msg = "⚡ on_select: %s" % args
        print({"On select message": msg})
        sublime.status_message(msg)


def checkNumber(text):
    value = None
    try:
        value = float(text)
        return True
    except Exception as e:
        sublime.status_message("👉"+str(e))  # status bar message
    return isinstance(value, float)

class SimpleInputHandler(sublime_plugin.TextInputHandler):
    def __init__(self, view):
        self.view = view

    def name(self): # args name to transport data in command.run(...)
        return "text"

    def placeholder(self): # a text show as backgroud of input box in GUI
        return "Text to insert" 

    def preview(self, text): # return some text/html preview on GUI
        return sublime.Html("<h1>{} :</h1>Selections: {}, Characters: {}"
                .format(self.__class__.__name__, len(self.view.sel()), len(text)))

class SimpleListInputHandler(sublime_plugin.ListInputHandler):
    def list_items(self):
        from html.entities import html5
        itemlist = sorted(html5.keys())
        selected_item_index = 2
        # return itemlist
        return (itemlist, selected_item_index)

    def preview(self, value):
        return sublime.Html("<h1>{} :</h1>Character: {}"
            .format(self.__class__.__name__, html5.get(value)))

class MultipleInputHandler(sublime_plugin.TextInputHandler):
    def __init__(self, view, names = None):
        self.view = view
        print("TPI __init__ names: %s" % (names))
        if(isinstance(names, tuple) or isinstance(names, list)):
            self._name, *self.next_names = names # destructuring assignment: "first" and "rest" 
        else:
            self._name, *self.next_names = [names]
        print("TPI __init__ _name: %s names: %s " % (self._name, self.next_names))
    
    def next_input(self, args):
        print("TPI next_input(self, args): %s %s" % (self.next_names, args))
        if self.next_names:
            self._name, *self.next_names = self.next_names
            return MultipleInputHandler(self.view, self._name)

    def name(self): 
        name = self._name if hasattr(self,'_name') else "text"
        print( "TPI name() return '%s'" % (name))
        return name # it may say plugin.run(self, edit, text)

    def placeholder(self):
        return "Type Number Here"

    def preview(self, text): # return preview when use typeing
        text = text or ""
        style = "border-bottom:2px solid #282828;opacity:0.2;padding-bottom: 4px"
        html = "<h1 style='{}'>{} :</h1>Selections: {} Characters: {} <hr> {}"
        name = self.__class__.__name__
        return sublime.Html(html.format(style,name,len(self.view.sel()), len(text), text))

    def want_event(self) -> bool:
        return True 
        # self.validate(v, event)
        # self.confirm(v, event)

    def confirm(self, text, event) -> None: # Just a notification
        print("confirm(self, text, event) text: %s event: %s" % (text,event))

    def validate(self, text, event): # Pass by return True 
        print("✒ validate(self, text, event): event: %s text: %s" % (event, text))
        return checkNumber(text)

    def cancel(self): # Press Esc to cancel
        print("cancel by user")

    def initial_text(self): # return text as a default value
        return "<h1>✒ Number multiple</h1>"

    def initial_selection(self): # Just prepares Selections
        # region = sublime.Region(2800,3028)
        region = self.view.find("gui_api_test", 1)
        regions = self.view.sel()
        regions.add(region)     # and new region at position between [2800,3028] 
        self.view.show(region)  # scroll view to the region
        return []
```
