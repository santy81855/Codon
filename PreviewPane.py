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
        # make the caret invisible
        self.setCaretWidth(0)
        # make line height smaller
        self.setExtraDescent(-6)
        # variable to track mouse clicking
        self.pressing = False
        self.start = 0
        # variable to store the position of teh textbox
        self.position = 0
    
    def getLexer(self):
        # get the file types
        fileType = config.tabArr[config.currentActiveTextBox].language
        
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
            lexer.setFont(font, 14)
            lexer.setFont(font, 15)
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
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        # call the normal mousemoveevent function so that we don't lose functionality
        #QsciScintilla.mouseMoveEvent(self, event)
        # if they are pressing then we want to scroll a certain amount for every pixel that we move
        if self.pressing:
            # store the starting position
            before = self.start
            # get the new position
            end = event.pos()
            # make this new position the starting position for the next movement
            self.start = end
            # get the difference in the y axis
            lines = end.y() - before.y()
            config.mainWin.textbox.SendScintilla(QsciScintilla.SCI_LINESCROLL, 0, int(lines/2))
            # ensure that both textboxes have the same first visible line at all times
            firstVisible = config.mainWin.textbox.firstVisibleLine()
            self.setFirstVisibleLine(firstVisible)
    
    def mousePressEvent(self, event):
        # set pressing to true
        self.pressing = True
        # store the position we pressed at
        self.start = event.pos()
        # store the position of the cursor when we clicked
        self.position = int(config.mainWin.textbox.SendScintilla(QsciScintilla.SCI_GETCURRENTPOS))
    
    def mouseReleaseEvent(self, event):
        self.pressing = False
        # place the cursor back where it was
        config.mainWin.textbox.setFocus()
        config.mainWin.textbox.SendScintilla(QsciScintilla.SCI_SETCURSOR, self.position)

    
    def mouseDoubleClickEvent(self, event):
        return
