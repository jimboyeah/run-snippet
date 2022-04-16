# 🚩 Readme Fist

学习 Sublime Text 插件开发，请参考 [Sublime API 探索](APIs.md)

了解 RunSnippetCommand 或 JumpTo 插件请继续阅读本文。


快捷键配置文件 RunSnippet\Default.sublime-keymap

```json
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
        "command": "show_panel",
        "keys": ["shift+escape"], 
        "args": {"panel": "output.exec"},
        "context": [ { "key": "panel_visible", "operand": true } ]
    },
    {
        "caption": "Jupm to ...",
        "command": "jump_to",
        "mnemonic": "j",
        "id": "jump_to",
        "keys": ["f9"], 
    },
]
```

## ⚡ RunSnippetCommand 插件

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


## ⚡ JumpTo ...

使用 SublimeText 阅读文档和写作是日常活动，特别是最近在阅读 [CPython](https://github.com/python/cpython) 以及 C# 相关开源代码及文档，Sublime 提供的跳转工具非常强大，因为会对代码文件进行符号索引，所以在已经建立索引的工程上，直接按 F12 就可以跳转到光标所在的符号定义上，对于 URL 地址，也可以通过右角菜单打开浏览器进行访问。

    git clone git@github.com:python/cpython
    git clone git@github.com:python/devguide
    git clone git@github.com:python/peps

不足的是，文档中有非常多的相对引用，这些引用都不能直接跳转到对应的文件中，需要通过 Ctrl+P 手动输入文件名间接跳转，对于大量文件查询来说，这是极其差的体验。

例如，C# 规范文档就包含许多文件，还有 .NET Core 和 ASP.NET Core 的参考文档中有大量示范代码文件的引用：

    - [ §1](csharp/standard/scope.md)  Scope
    - [ §2](csharp/standard/normative-references.md)  Normative references
    - [ §3](csharp/standard/terms-and-definitions.md)  Terms and definitions
    - [ §4](csharp/standard/general-description.md)  General description
    - [ §5](csharp/standard/conformance.md)  Conformance
    - [ §6](csharp/standard/lexical-structure.md)  Lexical structure
    - [ §7](csharp/standard/basic-concepts.md)  Basic concepts
    - [ §8](csharp/standard/types.md)  Types
    - [ §9](csharp/standard/variables.md)  Variables
    - [§10](csharp/standard/conversions.md)  Conversions
    - [§11](csharp/standard/expressions.md)  Expressions
    - [§12](csharp/standard/statements.md)  Statements
    - [§13](csharp/standard/namespaces.md)  Namespaces
    - [§14](csharp/standard/classes.md)  Classes
    - [§15](csharp/standard/structs.md)  Structs
    - [§16](csharp/standard/arrays.md)  Arrays
    - [§17](csharp/standard/interfaces.md)  Interfaces
    - [§18](csharp/standard/enums.md)  Enums
    - [§19](csharp/standard/delegates.md)  Delegates
    - [§20](csharp/standard/exceptions.md)  Exceptions
    - [§21](csharp/standard/attributes.md)  Attributes
    - [§22](csharp/standard/unsafe-code.md)  Unsafe code
    - [ §A](csharp/standard/grammar.md)  Grammar
    - [ §B](csharp/standard/portability-issues.md)  Portability issues
    - [ §C](csharp/standard/standard-library.md)  Standard library
    - [ §D](csharp/standard/documentation-comments.md)  Documentation comments
    - [ §E](csharp/standard/bibliography.md)  Bibliography

为此，有了开发 JumpTo 插件的想法，这是一个可以极高地提升文档阅读效率的插件，你值得拥有。

预期支持跳转地址格式如下：

- [x] 带括号的文件 (scope.md)
- [x] 带引号的文件 'scope.md' 或 "scope.md"
- [x] 带前导符号且使用空格分隔的文件路径
- [ ] 带 # 的设置的行号 (scope.md#LINE_NO)
- [ ] 带 # 的设置的标签 (scope.md#ANCHRO)

因为 Sublime 文件跳转有个临时状态，文件并没有完全确定打开，此时按方向键及回车之外的键，都会撤消文件的打开。所以，带标签的自动定位还需要寻求其它解决办法。

可跳转的内容示范：

    - language-reference\builtin-types\value-types.md
    - language-reference/builtin-types/value-types.md
    - [`is` expression](operators/is.md)
    # csharp\fundamentals\functional\pattern-matching.md
    :::code language="csharp" source="Program.cs" ID="NullableCheck":::

默认按 Shift 点击内容进行跳转，配置热键使用更方便。实现中使用了 on_text_command 事件，它可以获取鼠标点击坐标，但没有找到相应的 API 将坐标转换为 Text Point。

Sublime 使用 Ctrl 和 Alt 两个控制键分别用于增减选区，所以不太好直接使用它们。同时 Shift 也被用来做字符扩展选择，但是还是免强可用，最好还是配置按键触发，默认配置 F9 触发。

使用到正则字符串处理具，参考 CPython 文档：

    +-- Doc\howto
    |   • -- regex.rst          => Regular Expression HOWTO
    +-- Doc\library
    |   • - re.rst              => `re` --- Regular expression operations

JumpTo 插件参考代码：

```py
class JumpToCommand(TextCommand, ViewEventListener):

    def __init__(self, *args):
        if args and isinstance(args[0], View):
            self.view = args[0]
        Logger.message("init %s" % str(args))

    def run(self, edit, *args):
        file = self.parseline()
        self.jump(file)

    def jump(self, file):
        if file:
            self.view.window().run_command("show_overlay", 
            {"overlay":"goto", "show_file": True, "text":file.replace("\\","/")})

    def is_enabled(self, *args):
        Logger.message("jump to is_enabled %s" % str(args))
        return self.parseline() != None

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
```


# 🚩 .Net Core Sources

如何阅读 .Net Core 源代码？

第一手资源是官方文档仓库：

- https://github.com/dotnet/docs
- https://github.com/dotnet/standard
- https://github.com/dotnet/csharpstandard
- https://github.com/dotnet/dotnet-api-docs
- https://github.com/dotnet/AspNetCore.Docs

快捷源查询 .NET Framework 代码可以使用 Reference Source https://referencesource.microsoft.com/

.Net Core 有三个核心开源代码仓库，外加一个 ASP.NET Core 和 Roslyn，项目容量如下：

|        Projects        |     Repository    |  Size  | Files  | Folders |
|------------------------|-------------------|--------|--------|---------|
| .NET Runtime           | runtime-6.0.4     | 811 MB | 56,191 | 9,565   |
| .NET Core Runtime      | coreclr-3.1.24    | 529 MB | 30,146 | 6,180   |
| .NET Core Libraries    | corefx-3.1.24     | 201 MB | 20,880 | 2,930   |
| .NET Compiler Platform | roslyn-4.0.1      | 304 MB | 16,576 | 3,061   |
| ASP.NET Core           | aspnetcore-3.1.24 | 113 MB | 12,505 | 2,830   |

✅ .NET Runtime (Runtime) 

    git clone https://github.com/dotnet/runtime
    git clone git@github.com:dotnet/runtime.git

.NET is a cross-platform runtime for cloud, mobile, desktop, and IoT apps.

This repo contains the code to build the .NET runtime, libraries and shared host (dotnet) installers for all supported platforms, as well as the sources to .NET runtime and libraries.

✅ .NET Core Libraries (CoreFX) 

    git clone https://github.com/dotnet/corefx
    git clone git@github.com:dotnet/corefx.git

This repo is used for servicing PR's for .NET Core 2.1 and 3.1. Please visit us at https://github.com/dotnet/runtime

This repo contains the library implementation (called "CoreFX") for .NET Core. It includes System.Collections, System.IO, System.Xml, and many other components. 

✅ .NET Core Runtime (CoreCLR) 

    git clone https://github.com/dotnet/coreclr
    git clone git@github.com:dotnet/coreclr.git

CoreCLR is the runtime for .NET Core. It includes the garbage collector, JIT compiler, primitive data types and low-level classes.

This repo contains the runtime implementation for .NET Core. It includes RyuJIT, the .NET GC, and many other components. Runtime-specific library code (System.Private.CoreLib) lives in the CoreCLR repo. It needs to be built and versioned in tandem with the runtime.

The rest of CoreFX is agnostic of runtime-implementation and can be run on any compatible .NET runtime (e.g. CoreRT).

✅ ASP.NET Core (AspNetCore) 

    git clone https://github.com/dotnet/aspnetcore
    git clone git@github.com:dotnet/aspnetcore.git

ASP.NET Core 容量是最小的，但项目实在还是太大，有 566 csproj 文件，包含 251 单元工程测试在内，26 个解决方案 .sln 文件也不少。在 .\src 目录下面有很多子目录，每一个子目录都是一个子项目，每个子项目中都包含了一个解决方案。此外，还好些 MSBuild 工程文件，.debproj .javaproj .npmproj .pkgproj .proj .rpmproj .vcxproj .wixproj，这么多的工程类型是因为 ASP.NET Core 是基于 Web 的编程，涉及前端 JavaScript 脚本，NodeJS 以及 Java 等开发环境。

✅ Roslyn .NET compiler (roslyn) 

    git clone https://github.com/dotnet/roslyn
    git clone git@github.com:dotnet/roslyn.git

The .NET Compiler Platform, the Roslyn .NET compiler provides C# and Visual Basic languages with rich code analysis APIs.

Roslyn is the open-source implementation of both the C# and Visual Basic compilers with an API surface for building code analysis tools.

Roslyn 项目是 .NET 开源编译器，.NET 平台程序的执行模型的不同阶段有两个不同的编译器：一个叫 Roslyn 编译器，负责把 C# 和 VB 代码编译为程序集；另一个叫 RyuJIT 编译器，负责把程序集中的 IL 中间语言代码编译为机器码。

最初 C# 语言的编译器是用 C++ 编写的，后来微软推出了一个新的用 C# 自身编写的编译器：Roslyn，它属于自举编译器，即编译器用自身语言来实现自己。Roslyn 支持 C# 和 Visual Basic 代码编译，并提供丰富的代码分析 API，可以用它来做代码生成器。


# 🚩 CPython Source Code Layout
- Developer Guide: https://devguide.python.org/
- Exploring CPython’s Internals https://devguide.python.org/exploring/
- CPython Directory structure https://devguide.python.org/setup/#directory-structure
- The CPython Developer's Guide https://github.com/python/devguide

On average, PyPy with Just-in-Time Compiler (JIT), is 4.2 times faster than CPython

    "If you want your code to run faster, you should probably just use PyPy."
    -- Guido van Rossum (creator of Python)

CPython is the original Python implementation. PyPy is not a completely universal replacement for the stock CPython runtime. PyPy has always performed best with “pure” Python applications — i.e., applications written in Python and nothing else. Python packages that interface with C libraries, such as NumPy, have not fared as well due to the way PyPy emulates CPython’s native binary interfaces. 

PyPy’s developers have whittled away at this issue, and made PyPy more compatible with the majority of Python packages that depend on C extensions. Numpy, for instance, works very well with PyPy now. But if you want maximum compatibility with C extensions, use CPython.

基于 Rust 语言实现的解释器也值得探索，它可以通过 WebAssembly 将 Python 运行于 Web 浏览器上：

    git clone git@github.com:RustPython/RustPython.git
    git clone git@github.com:RustPython/rustpython.github.io.git

开发者参考文档 The CPython Developer's Guide，可以作为源代码开发者参考：

    git clone git@github.com:python/devguide

    +-- git clone git@github.com:python/devguide
    |   • -- index.rst                  => Python Developer's Guide
    |   • -- 1. setup.rst               => Getting Started
    |   • -- 2. help.rst                => Where to Get Help
    |   • -- 3. pullrequest.rst         => Lifecycle of a Pull Request
    |   • -- 4. runtests.rst            => Running & Writing Tests
    |   • -- 5. coverage.rst            => Increase Test Coverage
    |   • -- 6. docquality.rst          => Helping with Documentation
    |   • -- 7. documenting.rst         => Documenting Python
    |   • -- 8. silencewarnings.rst     => Silence Warnings From the Test Suite
    |   • -- 9. fixingissues.rst        => Fixing "easy" Issues (and Beyond)
    |   • -- 10. tracker.rst            => Issue Tracking
    |   • -- 11. triaging.rst           => Triaging an Issue
    |   • -- 12. communication.rst      => Following Python's Development
    |   • -- 13. porting.rst            => Porting Python to a new platform
    |   • -- 14. coredev.rst            => How to Become a Core Developer
    |   • -- 15. developers.rst         => Developer Log
    |   • -- 16. committing.rst         => Accepting Pull Requests
    |   • -- 17. devcycle.rst           => Development Cycle
    |   • -- 18. buildbots.rst          => Continuous Integration
    |   • -- 19. stdlibchanges.rst      => Adding to the Stdlib
    |   • -- 20. langchanges.rst        => Changing the Python Language
    |   • -- 21. experts.rst            => Experts Index
    |   • -- 22. gdb.rst                => gdb Support
    |   • -- 23. exploring.rst          => Exploring CPython's Internals
    |   • -- 24. grammar.rst            => Changing CPython's Grammar
    |   • -- 25. parser.rst             => Guide to CPython's Parser
    |   • -- 26. compiler.rst           => Design of CPython's Compiler
    |   • -- 27. garbage_collector.rst  => Design of CPython's Garbage Collector
    |   • -- 28. extensions.rst         => Updating standard library extension modules
    |   • -- 29. c-api.rst              => Changing Python's C API
    |   • -- 30. coverity.rst           => Coverity Scan
    |   • -- 31. clang.rst              => Dynamic Analysis with Clang
    |   • -- 32. buildworker.rst        => Running a buildbot worker
    |   • -- 33. motivations.rst        => Core Developer Motivations and Affiliations
    |   • -- 34. gitbootcamp.rst        => Git Bootcamp and Cheat Sheet
    |   • -- 35. appendix.rst           => Appendix: Topics 
    |   • -- README.rst                 => The CPython Developer's Guide

CPython Source Code Layout 源代码目录结构

```sh
# Install and set up Git and other dependencies 
# The latest release for each Python version can be found on the download page.
# https://www.python.org/downloads/
# Clone or fork the CPython repository to get the source code using:
git clone https://github.com/cpython/cpython
cd cpython
# Build Python, on UNIX and Mac OS use:
./configure --with-pydebug && make -j
# and on Windows use:
PCbuild\build.bat -e -d
# Run the tests:
./python -m test -j3
```

For Python modules, the typical layout is:

    Lib/<module>.py
    Modules/_<module>.c (if there’s also a C accelerator module)
    Lib/test/test_<module>.py
    Doc/library/<module>.rst

For extension-only modules, the typical layout is:

    Modules/<module>module.c
    Lib/test/test_<module>.py
    Doc/library/<module>.rst

For builtin types, the typical layout is:

    Objects/<builtin>object.c
    Lib/test/test_<builtin>.py
    Doc/library/stdtypes.rst

For builtin functions, the typical layout is:

    Python/bltinmodule.c
    Lib/test/test_builtin.py
    Doc/library/functions.rst

Some exceptions:

- • builtin type int is at ➡ Objects/longobject.c
- • builtin type str is at ➡ Objects/unicodeobject.c
- • builtin module sys is at ➡ Python/sysmodule.c
- • builtin module marshal is at ➡ Python/marshal.c
- • Windows-only module winreg is at ➡ PC/winreg.c

CPython Directory structure

- ➡ `Doc` The official documentation https://docs.python.org/.
- ➡ `Grammar` Contains the EBNF grammar file for Python.
- ➡ `Include` Contains all interpreter-wide header files.
- ➡ `Lib` The part of the standard library implemented in pure Python.
- ➡ `Mac` Mac-specific code (e.g., using IDLE as an OS X application).
- ➡ `Misc` Things that do not belong elsewhere. Typically this is varying kinds of developer-specific documentation.
- ➡ `Modules` The part of the standard library (plus some other code) that is implemented in C.
- ➡ `Objects` Code for all built-in types.
- ➡ `PC` Windows-specific code.
- ➡ `PCbuild` Build files for the version of MSVC currently used for the Windows installers provided on python.org.
- ➡ `Parser` Code related to the parser. The definition of the AST nodes is also kept here.
- ➡ `Programs` Source code for C executables, including the main function for the CPython interpreter (in versions prior to Python 3.5, these files are in the Modules directory).
- ➡ `Python` The code that makes up the core CPython runtime. This includes the compiler, eval loop and various built-in modules.
- ➡ `Tools` Various tools that are (or have been) used to maintain Python.

Python Misc subdirectory

    ========================

    This directory contains files that wouldn't fit in elsewhere.  Some
    documents are only of historic importance.

    Files found here
    ----------------

    ACKS                    Acknowledgements
    gdbinit                 Handy stuff to put in your .gdbinit file, if you use gdb
    HISTORY                 News from previous releases -- oldest last
    indent.pro              GNU indent profile approximating my C style
    NEWS                    News for this release (for some meaning of "this")
    Porting                 Mini-FAQ on porting to new platforms
    python-config.in        Python script template for python-config
    python.man              UNIX man page for the python interpreter
    python.pc.in            Package configuration info template for pkg-config
    python-wing*.wpr        Wing IDE project file
    README                  The file you're reading now
    README.AIX              Information about using Python on AIX
    README.coverity         Information about running Coverity's Prevent on Python
    README.valgrind         Information for Valgrind users, see valgrind-python.supp
    SpecialBuilds.txt       Describes extra symbols you can set for debug builds
    svnmap.txt              Map of old SVN revs and branches to hg changeset ids,
                            help history-digging
    valgrind-python.supp    Valgrind suppression file, see README.valgrind
    vgrindefs               Python configuration for vgrind (a generic pretty printer)


文档标题可以使用 PowerShell 读取：

```sh
$dir = "C:\Python-2.7.18\Doc\reference*.rst"
$dir = "C:\Python-3.10.2\Doc\howto\*.rst"
clear
(dir $dir) | % { 
    $rst = Get-Content "$dir\$($_.Name)"
    foreach ($line in $rst){
        # Title # Subtitle # Subtitle # Index
        if (-not ($line.StartsWith("******") `
            -or $line.StartsWith("------")   `
            -or $line.StartsWith("======")   `
            -or $line.StartsWith("######")   `
            ) ) 
        {
            if ($rst.IndexOf($line) -eq $rst.Count -1)
            {
                echo $_.name
            }
            continue
        }
        $idx = $rst.IndexOf($line)
        $title = $rst[$idx+1].Trim()
        if ($title -eq ""){ $title = $rst[$idx-1] }
        echo ("    |   • -- {0,-26} => $title" -f $_.Name)
        break
    }
}
```
