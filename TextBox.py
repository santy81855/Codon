import sys
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtGui import QCursor, QMouseEvent, QFont, QKeySequence, QSyntaxHighlighter, QTextCharFormat, QBrush, QTextCursor, QFontMetrics
from PyQt5.QtCore import QPoint, pyqtSignal, QRegExp
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve
from PyQt5.QtCore import QObject, QMimeData
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QCompleter, QFileDialog, QGraphicsDropShadowEffect
from PyQt5.QtWidgets import QHBoxLayout, QTextEdit, QPlainTextEdit, QShortcut
from PyQt5.QtWidgets import QLabel, QStackedWidget, QMessageBox
from PyQt5.QtWidgets import QPushButton, QDesktopWidget
from PyQt5.QtWidgets import QVBoxLayout, QScrollBar
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRect, QSize, QRectF
from PyQt5.QtWidgets import QWidget, QPlainTextEdit, QTextEdit
from PyQt5.QtGui import QColor, QPainter, QTextFormat, QLinearGradient, QImage
import textwrap
from pynput import keyboard
import string
import os
import subprocess
from pathlib import Path
import ctypes
import re
# to get the working monitor size
from win32api import GetMonitorInfo, MonitorFromPoint
from PyQt5.Qsci import QsciScintilla, QsciLexerPython, QsciLexerCPP, QsciLexerCSharp, QsciLexerJava, QsciLexerJavaScript, QsciLexerJSON
import TitleBar, Tab, WordCount, PreviewPane, TextBox, main
import config, ScrollBar

class Editor(QsciScintilla):
    ARROW_MARKER_NUM = 8
    def __init__(self, parent=None):
        super().__init__(parent)
        # set the color
        self.setPaper(QColor(config.backgroundColor))
        # set the background color
        self.setWhitespaceBackgroundColor(QColor(config.backgroundColor))
        self.setMouseTracking(True)
        # Set the default font
        font = QFont()
        font.setFamily('Consolas')
        font.setFixedPitch(True)
        font.setPointSize(config.fontSize)
        self.setFont(font)
        self.setMarginsFont(font)
         # Margin 0 is used for line numbers
        fontmetrics = QFontMetrics(font)
        self.setMarginsFont(font)
        self.setMarginsForegroundColor(QColor(config.lineNumberColor))
        self.setMarginWidth(0, fontmetrics.width("00000"))
        self.setMarginLineNumbers(0, True)
        self.setMarginsBackgroundColor(QColor(config.backgroundColor))
        self.setTabWidth(4)
        self.setAutoIndent(True)
        self.setColor(QColor(config.textColor))
        self.setEolMode(1)
        # Clickable margin 1 for showing markers
        self.setMarginSensitivity(1, True)
        self.markerDefine(QsciScintilla.RightArrow,
            self.ARROW_MARKER_NUM)
        self.setMarkerBackgroundColor(QColor(config.selectionColor),
            self.ARROW_MARKER_NUM)

        # set the selection colors
        self.setSelectionBackgroundColor(QColor(config.selectionColor))
        self.setSelectionForegroundColor(QColor(config.selectionTextColor))
        self.setCaretForegroundColor(QColor(config.lineNumberColor))

        # Current line visible with special background color
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor(config.curLineColor))
        # remove horizontal scroll bar
        self.SendScintilla(QsciScintilla.SCI_SETHSCROLLBAR, 0)
        # detect if lines changed
        self.cursorPositionChanged.connect(self.cursorChanged)
        # store if opening bracket was our last move
        self.wasBracket = False    
        # set the wrapmode so that text wraps 
        self.setWrapMode(QsciScintilla.WrapWord)
        # create a new scrollbar that looks nicer
        self.scrollbar = ScrollBar.ScrollBar(self)
        self.replaceVerticalScrollBar(self.scrollbar)
        self.horScrollbar = ScrollBar.ScrollBar(self)
        self.replaceHorizontalScrollBar(self.horScrollbar)

    def getLexer(self):
        # get the file types
        fileType = config.tabArr[config.currentActiveTextBox].language
        
        # Set the default font
        font = QFont()
        font.setFamily('Consolas')
        font.setFixedPitch(True)
        font.setPointSize(config.fontSize)
        self.setFont(font)
        self.setMarginsFont(font)
        # if we want to use syntax highlighting
        if fileType in config.keywords:
            if fileType == "py":
                lexer = QsciLexerPython()
                # change the background color
                lexer.setDefaultPaper(QColor(config.backgroundColor))
                # change the default text color
                lexer.setDefaultColor(QColor(config.textColor))
                # make the identifier(variable names) have the textcolor
                lexer.setColor(QColor(config.textColor), 11)
                # change the operator color (symbols)
                lexer.setColor(QColor(config.operatorColor), 10)
                # change the keyword color
                lexer.setColor(QColor(config.keywordColor), 5)
                # change the comment color (single, and block)
                lexer.setColor(QColor(config.commentColor), 1)
                lexer.setColor(QColor(config.commentColor), 6)
                # change function color
                lexer.setColor(QColor(config.functionColor), 9)
                # class name color
                lexer.setColor(QColor(config.classColor), 8)
                # change the string color
                lexer.setColor(QColor(config.stringColor), 4)
                lexer.setColor(QColor(config.stringColor), 3)
                lexer.setColor(QColor(config.stringColor), 7)
                lexer.setColor(QColor(config.stringColor), 13) # open string
                # change number color
                lexer.setColor(QColor(config.numberColor), 2)
                # decoration color
                lexer.setColor(QColor(config.stringColor), 15)
                # set fonts
                lexer.setFont(font, 1)
                lexer.setFont(font, 2)
                lexer.setFont(font, 3)
                lexer.setFont(font, 4)
                lexer.setFont(font, 5)
                lexer.setFont(font, 6)
                lexer.setFont(font, 7)
                lexer.setFont(font, 8)
                lexer.setFont(font, 9)
                lexer.setFont(font, 10)
                lexer.setFont(font, 11)
                lexer.setFont(font, 12)
                lexer.setFont(font, 13)
                lexer.setAutoIndentStyle(2)
            elif fileType == "c" or fileType == "cpp" or fileType == "java" or fileType == "js" or fileType == "cs":
                lexer = QsciLexerCPP()
                # change the background color
                lexer.setDefaultPaper(QColor(config.backgroundColor))
                # change the default text color
                lexer.setDefaultColor(QColor(config.textColor))
                # comment color
                lexer.setColor(QColor(config.commentColor), 1)
                lexer.setColor(QColor(config.commentColor), 1+64)
                # number
                lexer.setColor(QColor(config.numberColor), 4)
                lexer.setColor(QColor(config.numberColor), 4+64)
                # keyword
                lexer.setColor(QColor(config.keywordColor), 5)
                lexer.setColor(QColor(config.keywordColor), 5+64)
                # strings
                lexer.setColor(QColor(config.stringColor), 6)
                lexer.setColor(QColor(config.stringColor), 6+64)
                lexer.setColor(QColor(config.stringColor), 7)
                lexer.setColor(QColor(config.stringColor), 7+64)
                # operator
                lexer.setColor(QColor(config.operatorColor), 10)
                lexer.setColor(QColor(config.operatorColor), 10+64)
                # identifier
                lexer.setColor(QColor(config.textColor), 11)
                lexer.setColor(QColor(config.textColor), 11+64)
                # unclosed string
                lexer.setColor(QColor(config.unclosedString), 12)
                lexer.setColor(QColor(config.unclosedString), 12+64)
                # autoindent
                lexer.setAutoIndentStyle(QsciScintilla.AiOpening)
                # set fonts
                lexer.setFont(font, 1)
                lexer.setFont(font, 2)
                lexer.setFont(font, 3)
                lexer.setFont(font, 4)
                lexer.setFont(font, 5)
                lexer.setFont(font, 6)
                lexer.setFont(font, 7)
                lexer.setFont(font, 8)
                lexer.setFont(font, 9)
                lexer.setFont(font, 10)
                lexer.setFont(font, 11)
                lexer.setFont(font, 12)
                lexer.setFont(font, 13)

            elif fileType == "json":
                lexer = QsciLexerJSON()
                # change the background color
                lexer.setDefaultPaper(QColor(config.backgroundColor))
                # change the default text color
                lexer.setDefaultColor(QColor(config.textColor))
                # number color
                lexer.setColor(QColor(config.numberColor), 1)
                # string color
                lexer.setColor(QColor(config.stringColor), 2)
                # unclosed String
                lexer.setColor(QColor(config.unclosedString), 3)
                # comments
                lexer.setColor(QColor(config.commentColor), 6)
                lexer.setColor(QColor(config.commentColor), 7)
                # operator
                lexer.setColor(QColor(config.operatorColor), 8)
                # keyword
                lexer.setColor(QColor(config.keywordColor), 11)
                # property color
                lexer.setColor(QColor(config.keywordColor), 4)
                # set fonts
                lexer.setFont(font, 1)
                lexer.setFont(font, 2)
                lexer.setFont(font, 3)
                lexer.setFont(font, 4)
                lexer.setFont(font, 5)
                lexer.setFont(font, 6)
                lexer.setFont(font, 7)
                lexer.setFont(font, 8)
                lexer.setFont(font, 9)
                lexer.setFont(font, 10)
                lexer.setFont(font, 11)
                lexer.setFont(font, 12)
                lexer.setFont(font, 13)
            lexer.setDefaultFont(font)
            self.setLexer(lexer)
        else:
            lexer = QsciLexerPython()
            lexer.setDefaultFont(font)
            # change the background color
            lexer.setDefaultPaper(QColor(config.backgroundColor))
            # change the default text color
            lexer.setDefaultColor(QColor(config.textColor))
            # make the identifier(variable names) have the textcolor
            lexer.setColor(QColor(config.textColor), 1)
            lexer.setColor(QColor(config.textColor), 2)
            lexer.setColor(QColor(config.textColor), 3)
            lexer.setColor(QColor(config.textColor), 4)
            lexer.setColor(QColor(config.textColor), 5)
            lexer.setColor(QColor(config.textColor), 6)
            lexer.setColor(QColor(config.textColor), 7)
            lexer.setColor(QColor(config.textColor), 8)
            lexer.setColor(QColor(config.textColor), 9)
            lexer.setColor(QColor(config.textColor), 10)
            lexer.setColor(QColor(config.textColor), 11)
            lexer.setColor(QColor(config.textColor), 12)
            lexer.setColor(QColor(config.textColor), 13)
            # set fonts
            lexer.setFont(font, 1)
            lexer.setFont(font, 2)
            lexer.setFont(font, 3)
            lexer.setFont(font, 4)
            lexer.setFont(font, 5)
            lexer.setFont(font, 6)
            lexer.setFont(font, 7)
            lexer.setFont(font, 8)
            lexer.setFont(font, 9)
            lexer.setFont(font, 10)
            lexer.setFont(font, 11)
            lexer.setFont(font, 12)
            lexer.setFont(font, 13)
            self.setLexer(lexer)

    def mouseMoveEvent(self, event):
        if event.pos().x() < 80:
            QApplication.setOverrideCursor(Qt.ArrowCursor)
        else:    
            QApplication.setOverrideCursor(Qt.IBeamCursor)
        # call the normal mousemoveevent function so that we don't lose functionality
        QsciScintilla.mouseMoveEvent(self, event)
    
    def keyPressEvent(self, event):     
        if event.matches(QKeySequence.AddTab):
            config.mainWin.newTabEmpty()
        
        # get rid of the find menu when pressing escape
        elif event.key() == QtCore.Qt.Key_Escape:
            config.mainWin.isFind = False
            config.mainWin.findWin.hide()

        elif event.key() == 16777220:
            # first determine what type of character we are dealing with
            pos = self.getCursorPosition()
            line = pos[0]
            col = pos[1]
            self.setSelection(line, col, line, col-1)
            leftChar = self.selectedText()
            # place the cursor back where it was and get the right character
            self.setCursorPosition(line, col)
            self.setSelection(line, col, line, col+1)
            rightChar = self.selectedText()
            # put the cursor back in the original position
            self.setCursorPosition(line, col)
            if leftChar == "{":
                if rightChar == "}":
                    # place two enters
                    QsciScintilla.keyPressEvent(self, event)
                    QsciScintilla.keyPressEvent(self, event)
                    # get the position of the cursor after the two enters
                    pos = self.getCursorPosition()
                    line = pos[0]
                    col = pos[1]
                    # insert a tab between the braces
                    self.indent(line-1)
                    # move cursor to correct spot
                    self.setCursorPosition(line-1, col+1)
                # otherwise insert our own closing bracket and then move the cursor back to the
                # original position
                else:
                    self.insert("}")
                    self.setCursorPosition(line, col)
                    # place two enters
                    QsciScintilla.keyPressEvent(self, event)
                    QsciScintilla.keyPressEvent(self, event)
                    # get the position of the cursor after the two enters
                    pos = self.getCursorPosition()
                    line = pos[0]
                    col = pos[1]
                    # insert a tab between the braces
                    self.indent(line-1)
                    # move cursor to correct spot
                    self.setCursorPosition(line-1, col+1)
                    
            elif leftChar == "[":
                if rightChar == "]":
                    # place two enters
                    QsciScintilla.keyPressEvent(self, event)
                    QsciScintilla.keyPressEvent(self, event)
                    # get the position of the cursor after the two enters
                    pos = self.getCursorPosition()
                    line = pos[0]
                    col = pos[1]
                    # insert a tab between the braces
                    self.indent(line-1)
                    # move cursor to correct spot
                    self.setCursorPosition(line-1, col+1)
                # otherwise insert our own closing bracket and then move the cursor back to the
                # original position
                else:
                    self.insert("]")
                    self.setCursorPosition(line, col)
                    # place two enters
                    QsciScintilla.keyPressEvent(self, event)
                    QsciScintilla.keyPressEvent(self, event)
                    # get the position of the cursor after the two enters
                    pos = self.getCursorPosition()
                    line = pos[0]
                    col = pos[1]
                    # insert a tab between the braces
                    self.indent(line-1)
                    # move cursor to correct spot
                    self.setCursorPosition(line-1, col+1)
            elif leftChar == ":":
                # for this just press enter and indent
                QsciScintilla.keyPressEvent(self, event)
                pos = self.getCursorPosition()
                line = pos[0]
                col = pos[1]
                self.indent(line+1)
                # put the cursor at the end of the indentation
                self.setCursorPosition(line, col+1)
            else:
                return QsciScintilla.keyPressEvent(self, event)
        else:
            return QsciScintilla.keyPressEvent(self, event)
        
    def keyReleaseEvent(self, event):
        # update the current cursor position
        pos = self.getCursorPosition()
        config.mainWin.infobarlayout.itemAt(config.cursorPositionIndex).widget().setText("ln " + str(pos[0]+1) + ", col " + str(pos[1]+1))
        config.tabArr[config.currentActiveTextBox].curPos = self.getCursorPosition()
        # do all the setsave stuff here
        global isShortCut
        global tabArr
        # if the last thing pressed was a shortcut we don't really have to do anything since there
        # are no text differences to store
        if config.isShortCut:
            config.isShortCut = False
        # if it was not a shortcut then we store the text differences
        else:            
            config.tabArr[config.currentActiveTextBox].isSaved = False
            # update the values in the textbox array
            config.tabArr[config.currentActiveTextBox].contents = config.mainWin.textbox.text()
            # update the value of the preview box
            config.mainWin.previewbox.setText(config.mainWin.textbox.text() + config.fiveHundredNewlines)
            # update the word count
            text = config.tabArr[config.currentActiveTextBox].contents
            # use regex to split it into a list of words
            text = re.findall('[\w\-]+', text)
            # update the variable storing the wordcount of the tab 
            config.tabArr[config.currentActiveTextBox].wordCount = len(text)     
        # update the value of the word count
        config.mainWin.infobarlayout.itemAt(config.wordCountIndex).widget().setText(str(config.tabArr[config.currentActiveTextBox].wordCount))
        # ensure that both textboxes have the same first visible line at all times
        firstVisible = config.mainWin.textbox.firstVisibleLine()
        config.mainWin.previewbox.setFirstVisibleLine(firstVisible)
        first = self.firstVisibleLine()
        config.mainWin.previewbox.setFirstVisibleLine(first)
        return QsciScintilla.keyReleaseEvent(self, event)
    
    def wheelEvent(self, event):
        # intercept scrolls on the main textbox so that we can do the same for the previewbox
        QsciScintilla.wheelEvent(self, event)
        QsciScintilla.wheelEvent(config.mainWin.previewbox, event)
        first = self.firstVisibleLine()
        config.mainWin.previewbox.setFirstVisibleLine(first)
    
    # if the cursor position changes we want to make sure the preview tab has the same first
    # visible line
    def cursorChanged(self):
        first = self.firstVisibleLine()
        config.mainWin.previewbox.setFirstVisibleLine(first)
        config.tabArr[config.currentActiveTextBox].curPos = self.getCursorPosition()
        # do all the setsave stuff here
        global isShortCut
        global tabArr
        # if the last thing pressed was a shortcut we don't really have to do anything since there
        # are no text differences to store
        if config.isShortCut:
            config.isShortCut = False
        # if it was not a shortcut then we store the text differences
        else:            
            config.tabArr[config.currentActiveTextBox].isSaved = False
            # update the values in the textbox array
            config.tabArr[config.currentActiveTextBox].contents = config.mainWin.textbox.text()
            # update the value of the preview box
            config.mainWin.previewbox.setText(config.mainWin.textbox.text() + config.fiveHundredNewlines)
            # update the word count
            text = config.tabArr[config.currentActiveTextBox].contents
            # use regex to split it into a list of words
            text = re.findall('[\w\-]+', text)
            # update the variable storing the wordcount of the tab 
            config.tabArr[config.currentActiveTextBox].wordCount = len(text)     
        # update the value of the word count
        config.mainWin.infobarlayout.itemAt(config.wordCountIndex).widget().setText(str(config.tabArr[config.currentActiveTextBox].wordCount))

    
    def mousePressEvent(self, event):
        QsciScintilla.mousePressEvent(self, event)
        # update the cursor position
        pos = self.getCursorPosition()
        config.mainWin.infobarlayout.itemAt(config.cursorPositionIndex).widget().setText("ln " + str(pos[0]+1) + ", col " + str(pos[1]+1))
        

        