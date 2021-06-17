# -*- coding: utf-8 -*-

import os, sys, re

from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.Qsci import *

from .utils import *

#---------------------------------------------------------------#
class FeatureLexer(QsciLexerCustom):
    def __init__(self, parent):
        #QsciLexerCustom.__init__(self, parent)
        super().__init__(parent)

        self._styles = {
             0: 'Default',    #默认
             1: 'Comment',    #注释
             2: 'Section',    #节点
             3: 'Key',        #关键字
             4: 'Assignment', #赋值
             5: 'Value',      #值  
             }

        for key,value in self._styles.items():
             setattr(self, value, key)
        self._foldcompact = True
        
        tokens = ["功能:", "场景:", "场景大纲:", "例子:", "假如", "当", "那么", "而且", "但是"]
        
        self.tokens = [(token.encode('utf-8'), len(token.encode('utf-8'))) for token in tokens]
        
    def foldCompact(self):
         return self._foldcompact

    def setFoldCompact(self, enable):
         self._foldcompact = bool(enable)

    def language(self):
         return 'Config Files'

    def description(self, style):
         return self._styles.get(style, '')

    def defaultColor(self, style):
         if style == self.Default:
             return QColor('#000000')
         elif style == self.Comment:
             return QColor('#A0A0A0')
         elif style == self.Section:
             return QColor('#CC6600')
         elif style == self.Key:
             return QColor('#0000CC')
         elif style == self.Assignment:
             return QColor('#CC0000')
         elif style == self.Value:
             return QColor('#00CC00')
         return QsciLexerCustom.defaultColor(self, style)

    def defaultPaper(self, style):
         if style == self.Section:
             return QColor('#FFEECC')
         return QsciLexerCustom.defaultPaper(self, style)

    def defaultEolFill(self, style):
         if style == self.Section:
             return True
         return QsciLexerCustom.defaultEolFill(self, style)

    def defaultFont(self, style):
         if style == self.Comment:
             if sys.platform in ('win32', 'cygwin'):
                 return QFont('Comic Sans MS', 9)
             return QFont('Bitstream Vera Serif', 9)
         return QsciLexerCustom.defaultFont(self, style)
    
    
    def styleText(self, start, end):
         
         def first_spaces(line):
            for index in range(len(line)):
                ch = chr(line[index])
                if ch not in [' ', '\t']:
                    return index 
            return len(line)

         editor = self.editor()
         
         #if editor is None:
         #    return

         SCI = editor.SendScintilla
         GETFOLDLEVEL = QsciScintilla.SCI_GETFOLDLEVEL
         SETFOLDLEVEL = QsciScintilla.SCI_SETFOLDLEVEL
         HEADERFLAG = QsciScintilla.SC_FOLDLEVELHEADERFLAG
         LEVELBASE = QsciScintilla.SC_FOLDLEVELBASE
         NUMBERMASK = QsciScintilla.SC_FOLDLEVELNUMBERMASK
         WHITEFLAG = QsciScintilla.SC_FOLDLEVELWHITEFLAG
         
         source = ''
         if end > editor.length():
             end = editor.length()
         if end > start:
             source = bytearray(end - start)
             SCI(QsciScintilla.SCI_GETTEXTRANGE, start, end, source)
         if not source:
             return

         compact = self.foldCompact()

         index = SCI(QsciScintilla.SCI_LINEFROMPOSITION, start)
         if index > 0:
             pos = SCI(QsciScintilla.SCI_GETLINEENDPOSITION, index - 1)
             state = SCI(QsciScintilla.SCI_GETSTYLEAT, pos)
         else:
             state = self.Default

         self.startStyling(start, 0x1f)

         for line in source.splitlines(True):
            pos = 0 
            length = len(line)
            space_len = first_spaces(line)
            
            if length == space_len :
                #空行, 或者都是空格的行
                self.setStyling(length, self.Default)
            else: 
                if chr(line[0]) == '#':
                    #注释行只能首字母为#,不能跳过空格
                    state = self.Comment
                elif space_len > 0:
                    #前缀空格的处理
                    self.setStyling(space_len, self.Default)
                    pos += space_len

                #line_left是跳过空格后剩下的字符串, 一定不会为空    
                line_left = line[space_len:] 
                if chr(line_left[0]) == '@':
                    #标签行
                    state = self.Value
                else:     
                    #处理标签
                    for token, token_len in self.tokens:
                        if line_left.startswith(token):
                            self.setStyling(token_len, self.Key)
                            pos += token_len
                            state = self.Default

                #如果pos还没到length, 说明剩余的数据都是同一个模式的数据    
                if pos < length:
                    self.setStyling(length-pos, state)
            
            if state == self.Section:
                 level = LEVELBASE | HEADERFLAG
            elif index > 0:
                 lastlevel = SCI(GETFOLDLEVEL, index - 1)
                 if lastlevel & HEADERFLAG:
                     level = LEVELBASE + 1
                 else:
                     level = lastlevel & NUMBERMASK
            else:
                 level = LEVELBASE
            '''      
            if whitespace:
                 level |= WHITEFLAG
            if level != SCI(GETFOLDLEVEL, index):
                  SCI(SETFOLDLEVEL, index, level)
            '''
            index += 1

         if index > 0:
             lastlevel = SCI(GETFOLDLEVEL, index - 1)
             if lastlevel & HEADERFLAG:
                 level = LEVELBASE + 1
             else:
                 level = lastlevel & NUMBERMASK
         else:
             level = LEVELBASE

         lastlevel = SCI(GETFOLDLEVEL, index)
         SCI(SETFOLDLEVEL, index, level | lastlevel & ~NUMBERMASK)

#---------------------------------------------------------------#

class BakFeatureLexer(QsciLexerCustom):

    def __init__(self, parent):
        super().__init__(parent)

        # Default text settings
        # ----------------------
        self.setDefaultColor(QColor("#ff000000"))
        self.setDefaultPaper(QColor("#ffffffff"))
        self.setDefaultFont(QFont("Consolas", 14))

        # Initialize colors per style
        # ----------------------------
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
        
        # Indicator look and feel
        # ------------------------
        self.parent().indicatorDefine(QsciScintilla.HiddenIndicator, 0)
        self.parent().setIndicatorHoverStyle(QsciScintilla.PlainIndicator, 0)


    def language(self):
        return "SimpleLanguage"


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
        return ""

    def styleText(self, start, end):
        print(start, end)
        # 1. Initialize the styling procedure
        # ------------------------------------
        self.startStyling(start)

        # 2. Slice out a part from the text
        # ----------------------------------
        text = self.parent().text()[start:end]
        lines = text.split('\n')

        tokens = ["功能:", "场景:", "场景大纲:", "例子:", "假如", "当", "那么", "而且", "但是"]
        
        # 3. Tokenize the text
        # ---------------------
        p = re.compile(r"[*]\/|\/[*]|\s+|\w+|\W")

        # 'token_list' is a list of tuples: (token_name, token_len)
        #token_list = [(token, len(bytearray(token, "utf-8"))) for token in p.findall(text)]
        token_list = [(token, len(bytearray(token, "utf-8"))) for token in p.findall(text)]
        #print(token_list)
        # 4. Style the text
        # ------------------
        # 4.1 Check if multiline comment
        editor = self.parent()
        
        # 4.2 Style the text in a loop
        for i, token in enumerate(token_list):
            if token[0] in ["功能", "场景", "场景大纲", "例子", "假如", "当", "那么", "而且", "但是"]:
                # cyan
                self.setStyling(token[1], 18)

            elif token[0] in ["#",]:
                # blue <b>
                self.setStyling(token[1], 13)
            else:
                # Default style
                self.setStyling(token[1], 0)
            ###
        
#---------------------------------------------------------------#
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
        
    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.isFocus = False
        
#---------------------------------------------------------------#
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
        
#---------------------------------------------------------------#
class PythonEditor(CustomEditor):
    
    def __init__(self, parent = None, panel = None):
        super().__init__(parent, panel)

        lexer = QsciLexerPython()
        self.setLexer(lexer)

        text = bytearray(str.encode("Arial"))# 32, "Courier New"         
        self.SendScintilla(QsciScintilla.SCI_STYLESETFONT, 1, text)
