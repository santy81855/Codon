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
import config

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
        font.setPointSize(14)
        self.setFont(font)
        self.setMarginsFont(font)
         # Margin 0 is used for line numbers
        fontmetrics = QFontMetrics(font)
        self.setMarginsFont(font)
        self.setMarginsForegroundColor(QColor(config.lineNumberColor))
        self.setMarginWidth(0, fontmetrics.width("00000"))
        self.setMarginLineNumbers(0, True)
        self.setMarginsBackgroundColor(QColor(config.backgroundColor))
        self.setTabIndents(True)
        self.setIndentationsUseTabs(True)
        self.setIndentationWidth(4)
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
        # remove vertical scroll bar
        self.SendScintilla(QsciScintilla.SCI_SETVSCROLLBAR, 0)
        # auto indent
        self.setAutoIndent(True)
        # detect if lines changed
        self.cursorPositionChanged.connect(self.cursorChanged)
        # store if opening bracket was our last move
        self.wasBracket = False    

    def getLexer(self):
        # get the file types
        fileType = config.tabArr[config.currentActiveTextBox].language
        
        # Set the default font
        font = QFont()
        font.setFamily('Consolas')
        font.setFixedPitch(True)
        font.setPointSize(14)
        self.setFont(font)
        self.setMarginsFont(font)
        # if we want to use syntax highlighting
        if fileType in config.keywords:
            if fileType == "py":
                lexer = QsciLexerPython()
            elif fileType == "c" or fileType == "cpp":
                lexer = QsciLexerCPP()
            elif fileType == "java":
                lexer = QsciLexerJava()
            elif fileType == "cs":
                lexer = QsciLexerCSharp()
            elif fileType == "js":
                lexer = QsciLexerJavaScript()
            elif fileType == "json":
                lexer = QsciLexerJSON
            lexer.setDefaultFont(font)
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
        # store the position of the cursor everytime we type
        config.tabArr[config.currentActiveTextBox].curPos = int(self.SendScintilla(QsciScintilla.SCI_GETCURRENTPOS))
        
        if event.matches(QKeySequence.AddTab):
            config.mainWin.newTabEmpty()
        
        elif event.key() == 16777220:
            if self.wasBracket == True:
                # do 1 enter
                QsciScintilla.keyPressEvent(self, event)
                pos = self.getCursorPosition()
                # add an indent
                self.indent(pos[0])
                # put the cursor at the end of the indent
                self.setCursorPosition(pos[0], pos[1] + config.TAB_SIZE)
                self.wasBracket = False
            else:
                return QsciScintilla.keyPressEvent(self, event)
        
        else:
            if event.text() == '{':
                self.wasBracket = True
            else:
                # set the bracket false by default
                self.wasBracket = False
            return QsciScintilla.keyPressEvent(self, event)
        
    def keyReleaseEvent(self, event):
        # update the current cursor position
        pos = self.getCursorPosition()
        config.mainWin.infobarlayout.itemAt(config.cursorPositionIndex).widget().setText("ln " + str(pos[0]+1) + ", col " + str(pos[1]+1))
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
        # make the active line on the previewbox the same

    
    def mousePressEvent(self, event):
        QsciScintilla.mousePressEvent(self, event)
        # update the cursor position
        pos = self.getCursorPosition()
        config.mainWin.infobarlayout.itemAt(config.cursorPositionIndex).widget().setText("ln " + str(pos[0]+1) + ", col " + str(pos[1]+1))
        

        