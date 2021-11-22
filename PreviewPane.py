import sys
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtGui import QCursor, QMouseEvent, QFont, QKeySequence, QSyntaxHighlighter, QTextCharFormat, QBrush, QTextCursor
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
import TitleBar, Tab, WordCount, PreviewPane, TextBox, main, config

class TextPreview(QsciScintilla):
    def __init__(self, parent):
        super(TextPreview, self).__init__()
        self.parent = parent
        self.setMouseTracking(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setPaper(QColor(config.backgroundColor))
        self.setMarginsBackgroundColor(QColor(config.backgroundColor))
        self.setReadOnly(True)
        self.setColor(QColor(config.textColor))
        # we want this one to not be selectable
        self.setSelectionBackgroundColor(QColor(config.backgroundColor))
    
    def getLexer(self):
        # get the file types
        fileType = config.tabArr[config.currentActiveTextBox].getFileType()
        
        # Set the default font
        font = QFont()
        font.setFamily('Consolas')
        font.setFixedPitch(True)
        font.setPointSize(4)
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
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        # call the normal mousemoveevent function so that we don't lose functionality
        QsciScintilla.mouseMoveEvent(self, event)