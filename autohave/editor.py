# -*- coding: utf-8 -*-

import os, sys, re

from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.Qsci import *

from .utils import *

#---------------------------------#
class FeatureLexer(QsciLexerCustom):

    def __init__(self, parent):
        super().__init__(parent)

        # Default text settings
        # ----------------------
        self.setDefaultColor(QColor("#ff000000"))
        self.setDefaultPaper(QColor("#ffffffff"))
        self.setDefaultFont(QFont("Consolas", 14))

        # Initialize colors per style
        # ----------------------------
        self.setColor(QColor("#ff" + "000000"), 0)  # black
        self.setColor(QColor("#ff" + "000000"), 1)  # black <b>
        self.setColor(QColor("#ff" + "d60404"), 2)  # red
        self.setColor(QColor("#ff" + "d60404"), 3)  # red <b>
        self.setColor(QColor("#ff" + "ff7f00"), 4)  # orange
        self.setColor(QColor("#ff" + "ff7f00"), 5)  # orange <b>
        self.setColor(QColor("#ff" + "ba9b00"), 6)  # yellow
        self.setColor(QColor("#ff" + "ba9b00"), 7)  # yellow <b>
        self.setColor(QColor("#ff" + "20ad20"), 8)  # lightgreen
        self.setColor(QColor("#ff" + "20ad20"), 9)  # lightgreen <b>
        self.setColor(QColor("#ff" + "005900"), 10)  # green
        self.setColor(QColor("#ff" + "005900"), 11)  # green <b>
        self.setColor(QColor("#ff" + "0202ce"), 12)  # blue
        self.setColor(QColor("#ff" + "0202ce"), 13)  # blue <b>
        self.setColor(QColor("#ff" + "9400d3"), 14)  # lightpurple
        self.setColor(QColor("#ff" + "9400d3"), 15)  # lightpurple <b>
        self.setColor(QColor("#ff" + "4b0082"), 16)  # purple
        self.setColor(QColor("#ff" + "4b0082"), 17)  # purple <b>
        self.setColor(QColor("#ff" + "0668d1"), 18)  # cyan
        self.setColor(QColor("#ff" + "0668d1"), 19)  # cyan <b>

        # Initialize paper colors per style
        # ----------------------------------
        self.setPaper(QColor("#ffffffff"), 0)  # white
        self.setPaper(QColor("#ffffffff"), 1)  # white
        self.setPaper(QColor("#ffffffff"), 2)  # white
        self.setPaper(QColor("#ffffffff"), 3)  # white
        self.setPaper(QColor("#ffffffff"), 4)  # white
        self.setPaper(QColor("#ffffffff"), 5)  # white
        self.setPaper(QColor("#ffffffff"), 6)  # white
        self.setPaper(QColor("#ffffffff"), 7)  # white
        self.setPaper(QColor("#ffffffff"), 8)  # white
        self.setPaper(QColor("#ffffffff"), 9)  # white
        self.setPaper(QColor("#ffffffff"), 10)  # white
        self.setPaper(QColor("#ffffffff"), 11)  # white
        self.setPaper(QColor("#ffffffff"), 12)  # white
        self.setPaper(QColor("#ffffffff"), 13)  # white
        self.setPaper(QColor("#ffffffff"), 14)  # white
        self.setPaper(QColor("#ffffffff"), 15)  # white
        self.setPaper(QColor("#ffffffff"), 16)  # white
        self.setPaper(QColor("#ffffffff"), 17)  # white
        self.setPaper(QColor("#ffffffff"), 18)  # white
        self.setPaper(QColor("#ffffffff"), 19)  # white

        # Initialize fonts per style
        # ---------------------------
        self.setFont(QFont("Consolas", 13, ), 0)
        self.setFont(QFont("Consolas", 13, weight=QFont.Bold), 1)
        self.setFont(QFont("Consolas", 13, ), 2)
        self.setFont(QFont("Consolas", 13, weight=QFont.Bold), 3)
        self.setFont(QFont("Consolas", 13, ), 4)
        self.setFont(QFont("Consolas", 13, weight=QFont.Bold), 5)
        self.setFont(QFont("Consolas", 13, ), 6)
        self.setFont(QFont("Consolas", 13, weight=QFont.Bold), 7)
        self.setFont(QFont("Consolas", 13, ), 8)
        self.setFont(QFont("Consolas", 13, weight=QFont.Bold), 9)
        self.setFont(QFont("Consolas", 13, ), 10)
        self.setFont(QFont("Consolas", 13, weight=QFont.Bold), 11)
        self.setFont(QFont("Consolas", 13, ), 12)
        self.setFont(QFont("Consolas", 13, weight=QFont.Bold), 13)
        self.setFont(QFont("Consolas", 13, ), 14)
        self.setFont(QFont("Consolas", 13, weight=QFont.Bold), 15)
        self.setFont(QFont("Consolas", 13, ), 16)
        self.setFont(QFont("Consolas", 13, weight=QFont.Bold), 17)
        self.setFont(QFont("Consolas", 13, ), 18)
        self.setFont(QFont("Consolas", 13, weight=QFont.Bold), 19)

        
        # Indicator look and feel
        # ------------------------
        self.parent().indicatorDefine(QsciScintilla.HiddenIndicator, 0)
        self.parent().setIndicatorHoverStyle(QsciScintilla.PlainIndicator, 0)

    ''''''

    def language(self):
        return "SimpleLanguage"

    ''''''

    def description(self, style):
        if style == 0:
            return "black"
        elif style == 1:
            return "black <b>"
        elif style == 2:
            return "red"
        elif style == 3:
            return "red <b>"
        elif style == 4:
            return "orange"
        elif style == 5:
            return "orange <b>"
        elif style == 6:
            return "yellow"
        elif style == 7:
            return "yellow <b>"
        elif style == 8:
            return "lightgreen"
        elif style == 9:
            return "lightgreen <b>"
        elif style == 10:
            return "green"
        elif style == 11:
            return "green <b>"
        elif style == 12:
            return "blue"
        elif style == 13:
            return "blue <b>"
        elif style == 14:
            return "lightpurple"
        elif style == 15:
            return "lightpurple <b>"
        elif style == 16:
            return "purple"
        elif style == 17:
            return "purple <b>"
        elif style == 18:
            return "cyan"
        elif style == 19:
            return "cyan <b>"
        ###
        return ""

    ''''''

    def styleText(self, start, end):
    
        # 1. Initialize the styling procedure
        # ------------------------------------
        self.startStyling(start)

        # 2. Slice out a part from the text
        # ----------------------------------
        text = self.parent().text()[start:end]

        # 3. Tokenize the text
        # ---------------------
        p = re.compile(r"[*]\/|\/[*]|\s+|\w+|\W")

        # 'token_list' is a list of tuples: (token_name, token_len)
        token_list = [(token, len(bytearray(token, "utf-8"))) for token in p.findall(text)]

        # 4. Style the text
        # ------------------
        # 4.1 Check if multiline comment
        editor = self.parent()
        
        # 4.2 Style the text in a loop
        for i, token in enumerate(token_list):
            if token[0] in ["功能:", "场景:", "假如", "当", "那么", "而且", "但是"]:
                # cyan
                self.setStyling(token[1], 18)

            elif token[0] in ["#",]:
                # blue <b>
                self.setStyling(token[1], 13)
            else:
                # Default style
                self.setStyling(token[1], 0)
            ###
        
    ''''''        
#---------------------------------#
class CustomEditor(QsciScintilla):
    ARROW_MARKER_NUM = 8

    def __init__(self, parent = None, panel = None):
        super().__init__(parent)
        
        self.panel = panel
        
        self.setEolMode(QsciScintilla.EolUnix)
        #self.setEolVisibility(True)
        
        # Set the default font
        font = QFont()
        font.setFamily('Courier New')
        font.setFixedPitch(True)
        font.setPointSize(12)
        
        self.setFont(font)
        self.setMarginsFont(font)
        self.setUtf8(True)  
        
        self.setIndentationsUseTabs(False)
        self.setTabWidth(4)
        self.setIndentationGuides(True)
        self.setTabIndents(True)
        #self.setAutoIndent(True)
        
        # Margin 0 is used for line numbers
        fontmetrics = QFontMetrics(font)
        self.setMarginsFont(font)
        self.setMarginWidth(0, fontmetrics.width("0000") + 4)
        self.setMarginLineNumbers(0, True)
        self.setMarginsBackgroundColor(QColor("#cccccc"))

        # Clickable margin 1 for showing markers
        self.setMarginSensitivity(1, True)
        self.markerDefine(QsciScintilla.RightArrow,
            self.ARROW_MARKER_NUM)
        self.setMarkerBackgroundColor(QColor("#ee1111"),
            self.ARROW_MARKER_NUM)

        # Brace matching: enable for a brace immediately before or after
        # the current position
        #
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)

        # Current line visible with special background color
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#ffe4e4"))
        
        self.isFocus = False
        
    def on_margin_clicked(self, nmargin, nline, modifiers):
        # Toggle marker for the line the margin was clicked on
        if self.markersAtLine(nline) != 0:
            self.markerDelete(nline, self.ARROW_MARKER_NUM)
        else:
            self.markerAdd(nline, self.ARROW_MARKER_NUM)
    
    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.isFocus = True
        #print('focusInEvent', event)
    
    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.isFocus = False
        #print('focusOutEvent', event)
        
#---------------------------------#
class FeatureEditor(CustomEditor):
    
    def __init__(self, parent = None, panel = None):
        super().__init__(parent, panel)
        self.line_index = None
        
        lexer = FeatureLexer(self)
        self.setLexer(lexer)
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.onContextMenu)
        
    def onContextMenu(self, pos):
        menu = QMenu()
        
        self.line_index = build_feature_index(self.text())
        cursor_pos = self.getCursorPosition()
        
        line_num = cursor_pos[0]+1
        if line_num not in self.line_index:
            return
            
        self.select_item = self.line_index[line_num]
        print(self.select_item)
        
        #self.genCodeAction = menu.addAction("GenCode")
        #self.genCodeAction.triggered.connect(self.onGenCode)
        
        #if self.select_item[0] == 'feature':
        #    self.renameFeatureAction = menu.addAction("Rename Feature")
        #    self.renameFeatureAction.triggered.connect(self.onRenameFeature)
        
        if self.select_item[0] == 'scenario':
            self.genCodeAction = menu.addAction("生成框架代码")
            self.genCodeAction.triggered.connect(self.onGenCode)
        
        elif self.select_item[0] == 'step':
            self.codeAction = menu.addAction("生成/显示代码")
            self.codeAction.triggered.connect(self.onShowOrGenCode)
        
        menu.exec_(self.viewport().mapToGlobal(pos))
    
    def onShowOrGenCode(self):
        step = self.select_item[1]
        match_code_str = f"@{step.step_type}.*\(.*['\"]{step.name}['\"].*\).*\n.*def.*\n"
        if not self.panel.locateCode(match_code_str, show = True):
            code_str = f'\n@{step.step_type}("{step.name}")\ndef step_impl(context):\n    pass\n'
            self.panel.appendCode(code_str)
    
    def onGenCode(self):
        for step in self.select_item[1].steps:
            match_code_str = f"@{step.step_type}.*\(.*['\"]{step.name}['\"].*\).*\n.*def.*\n"
            if not self.panel.locateCode(match_code_str, show = False):
                code_str = f'\n@{step.step_type}("{step.name}")\ndef step_impl(context):\n    pass\n'
                self.panel.appendCode(code_str)
    
    def onRenameFeature(self):
        pass
        
#---------------------------------#
class PythonEditor(CustomEditor):
    
    def __init__(self, parent = None, panel = None):
        super().__init__(parent, panel)

        lexer = QsciLexerPython()
        self.setLexer(lexer)

        text = bytearray(str.encode("Arial"))# 32, "Courier New"         
        self.SendScintilla(QsciScintilla.SCI_STYLESETFONT, 1, text)