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
from PyQt5.QtGui import QColor, QPainter, QTextFormat, QLinearGradient
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
        self.setIndentationWidth(4)
        self.setColor(QColor(config.textColor))
        self.setEolMode(1)
        # Clickable margin 1 for showing markers
        self.setMarginSensitivity(1, True)
        self.markerDefine(QsciScintilla.RightArrow,
            self.ARROW_MARKER_NUM)
        self.setMarkerBackgroundColor(QColor(config.selectionColor),
            self.ARROW_MARKER_NUM)
    
        self.setSelectionBackgroundColor(QColor(config.selectionColor))
        self.setSelectionForegroundColor(QColor(config.selectionTextColor))
        self.setCaretForegroundColor(QColor(config.lineNumberColor))

        # Current line visible with special background color
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor(config.curLineColor))
        # remove horizontal scroll bar
        self.SendScintilla(QsciScintilla.SCI_SETHSCROLLBAR, 0)
        # auto indent
        self.setAutoIndent(True)
    
    def getLexer(self):
        # get the file types
        fileType = config.tabArr[config.currentActiveTextBox].getFileType()
        
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
            # change the keyword color
            lexer.setColor(QColor(config.keywordColor), 5)
            # change the comment color (single, and block)
            lexer.setColor(QColor(config.commentColor), 1)
            lexer.setColor(QColor(config.commentColor), 6)
            # change function color
            lexer.setColor(QColor(config.functionColor), 9)
            # change the quote color
            lexer.setColor(QColor(config.stringColor), 4)
            lexer.setColor(QColor(config.stringColor), 3)
            lexer.setColor(QColor(config.stringColor), 7)
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
        else:
            return QsciScintilla.keyPressEvent(self, event)

        