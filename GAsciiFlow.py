from __future__ import annotations
import enum
from time import time
import typing
from typing import List, Union
import re


class ListStr(List[str]):
    pass

# Python 3.12 new keyword: type
# type ListStr = list[str]

class GAF(enum.Enum):
    AsciiFlow = "AsciiFlow"
    Known = ""
    # TODO: more graphic type

    @classmethod
    def fromStr(cls, val:str):
        if val == GAF.AsciiFlow.value:
            return GAF.AsciiFlow
        return GAF.Known


class TagType(enum.Enum):
    Box = "BOX"
    Text = "TEXT"
    UnInit = "uninit"
    Known = ""

    @classmethod
    def list(cls) -> List[str]:
        return [TagType.Box.value, TagType.Text.value, ]

    @classmethod
    def fromStr(cls, val:str):
        if val == TagType.Box.value:
            return TagType.Box
        if val == TagType.Text.value:
            return TagType.Text
        return TagType.Known

    # Type hint of a method with the type of the enclosing class
    # Python 3.7 - PEP 563 -- Postponed Evaluation of Annotations
    # Python 3.7+: from __future__ import annotations
    # Python <3.7: use a string
    @classmethod
    def new(cls, T:str) -> Union[BoxTag, TextTag, KnownTag]:
        if T == TagType.Box.value:
            return BoxTag()
        if T == TagType.Text.value:
            return TextTag()
        return KnownTag()


class Tag:
    # Python Tutorial - Class and Instance Variables
    # https://docs.python.org/3/tutorial/classes.html
    ID: str
    width: int = 0
    height: int = 0
    x: int = 0
    y: int = 0
    type: TagType = TagType.UnInit
    socketOut: list[str]
    socketIn: list[str]
    socketInOut: list[str]
    text: list[str]
    attributes: dict[str, str]

    def __init__(self, ID="_", type=None):
        self.ID = ID
        if type is not None:
            self.type = type
        self.socketOut = []
        self.socketIn = []
        self.socketInOut = []
        self.text = []
        self.attributes = dict()

    def __str__(self):
        type = self.type
        ID = self.ID
        w = self.width
        h = self.height
        text = self.text
        In = self.socketIn
        Out = self.socketOut
        InOut = self.socketInOut
        return f'<{type}:{ID} text:{text} w:{w} w:{h} In:{In} Out:{Out} InOut:{InOut}>'

    def appendText(self, value: str):
        self.text.append(value)

    def setAtts(self, name:str, value: str):
        self.attributes[name] = value

    def addSocketOut(self, target:str):
        self.socketOut.append(target)

    def addSocketIn(self, target:str):
        self.socketIn.append(target)

    def addSocketInOut(self, target:str):
        self.socketInOut.append(target)

class KnownTag(Tag):
    type = TagType.Known

class BoxTag(Tag):
    type = TagType.Box

class TextTag(Tag):
    type = TagType.Text


class Render:
    graph:GAsciiFlow

class AsciiFlowRener(Render):
    symbols = "╔╗╚╝═║╩╦╣╠╬↑↓←→⇆⇅"
    graph:AsciiFlow

    def __init__(self, asciiFlow: AsciiFlow):
        self.graph = asciiFlow

    def __call__(self):
        return self.render()

    def render(self):
        return [str(self.graph.tags[it]) for it in self.graph.tags]


class GAsciiFlow:

    type: GAF = GAF.Known

    def __init__(self, grammar:str, lines:list[str]):
        print("GAsciiFlow: ", lines[0:2])

    def render(self):
        return("Unimplemented GAsciiFlow render.")

    @classmethod
    def parse(cls, grammar:str):
        lines = grammar.strip().split('\n')
        if lines[0].strip() == "":
            del lines[0]

        if lines[0][0:4] != "GAF:":
            raise Exception("Not valid GAsciiFlow grammar code. A GAF: tag is expected at beginning.", grammar)

        it = GAF.fromStr(lines[0][4:].strip())

        # print("GAF Graphic Type: ", it)
        if it == GAF.AsciiFlow:
            return AsciiFlow(grammar, lines[1:])
        return GAsciiFlow('', [])


class AsciiFlow(GAsciiFlow):

    tags: dict = dict()
    ids: set[str] = set()
    type: GAF = GAF.AsciiFlow

    def __init__(self, grammar:str, lines:list[str]):
        self.parseTags(grammar, lines)

    def render(self):
        render = AsciiFlowRener(self)
        return render()

    def parseTags(self, grammar:str, lines:list[str]):
        while len(lines):
            it = lines[0]
            del lines[0]
            tk = re.split(' +', it)
            nm = tk[0][0:-1]
            tag = TagType.new(nm)

            if tag.type == TagType.Known:
                raise Exception(f"Unsupported tag, {nm}, {TagType.list()} was expeacted.")

            if len(tk) > 3 and tk[2] not in ["->", "<-", "<->"]:
                tag.ID = tk[2].strip()
            elif len(tk) > 3:
                ID = tk[3]
                arrow = tk[2]
                self.ids.add(ID)
                if arrow == "->":
                    tag.addSocketOut(ID)
                elif arrow == "<-":
                    tag.addSocketIn(ID)
                elif arrow == "<->":
                    tag.addSocketInOut(ID)
            
            if len(tk)>1:
                tag.ID = tk[1]

            that = self.tags.get(tag.ID)
            self.ids.add(tag.ID)
            if that:
                print(self.tags)
                raise Exception(f"Tag {tag.ID} already existing: {that} => {tag}")
            else:
                self.tags[tag.ID] = tag
            self.parseTagAtts(tag, lines)
            # print("Parse Tag: ", tag.ID, tag, it)

        for it in self.ids:
            if self.tags.get(it) is None:
                raise Exception(f'Tag not found: {it}')

    def parseTagAtts(self, tag: Tag, lines:list[str]):

        while len(lines):
            it = lines[0]
            if not it.startswith(" ") or it.strip() != "":
                break
            del lines[0]
            it = it.strip()
            att = it.split(':')
            if it.startswith(":") and len(att) > 2:
                tag.setAtts(att[1], ":".join(att[2:]));

        while len(lines):
            it = lines[0]
            if not it.startswith(' ') and it != "":
                break
            del lines[0]
            if it != "":
                tag.height += 1
                txt = it.strip()
                if tag.width < len(txt):
                    tag.width = len(txt)
                tag.appendText(txt)


if __name__ == '__main__':
    example = """
GAF: AsciiFlow
BOX: A   ->   C
    Macintosh
    application

BOX: B -> D
    Windows
    application

TEXT: C -> E
    QuickDraw

TEXT: D -> E
    GDI

BOX: E
    PDF Writer

TEXT: F
    PDF

BOX: G
    Acrobat Exchange or Reader

"""
    # Figure 2.2 Creating PDF files using the Distiller program

    flow = GAsciiFlow.parse(example)
    rendered = flow.render()
    print(rendered)