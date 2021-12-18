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
import TitleBar, Tab, WordCount, PreviewPane, TextBox, main, config, ScrollBar

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
        #self.setCaretWidth(0)
        self.SendScintilla(QsciScintilla.SCI_SETCARETPERIOD, 0)
        # make line height smaller
        self.setExtraDescent(-7)
        self.setExtraAscent(-7)
        
        # variable to track mouse clicking
        self.pressing = False
        # variable to store the position of teh textbox
        self.position = 0
    
    def getLexer(self):
        # get the file types
        fileType = config.tabArr[config.currentActiveTextBox].language
        
        # Set the default font
        font = QFont()
        font.setFamily('Consolas')
        font.setFixedPitch(True)
        font.setPointSize( 4 )
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
                #lexer.setColor(QColor(config.commentColor), 1)
                #lexer.setColor(QColor(config.commentColor), 1+64)
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
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        if config.isSnapWidget == True:
            self.parent.snapWidget.hide()
            config.isSnapWidget = False
        # call the normal mousemoveevent function so that we don't lose functionality
        #QsciScintilla.mouseMoveEvent(self, event)
        # if they are pressing then we want to scroll a certain amount for every pixel that we move
        if self.pressing:
            # calculate the amount of pixels we just moved in terms of the scrollbar
            ratio = event.pos().y() / self.height()
            sliderPosition = ratio * config.mainWin.textbox.scrollbar.maximum()
            config.mainWin.textbox.scrollbar.setSliderPosition(sliderPosition)
            # ensure that both textboxes have the same first visible line at all times
            firstVisible = config.mainWin.textbox.firstVisibleLine()
            self.setFirstVisibleLine(firstVisible)
    
    def mousePressEvent(self, event):
        ratio = event.pos().y() / self.height()
        sliderPosition = ratio * config.mainWin.textbox.scrollbar.maximum()
        config.mainWin.textbox.scrollbar.setSliderPosition(sliderPosition)
        # ensure that both textboxes have the same first visible line at all times
        firstVisible = config.mainWin.textbox.firstVisibleLine()
        self.setFirstVisibleLine(firstVisible)
        # set pressing to true
        self.pressing = True
        # store the position of the cursor when we clicked
        self.position = int(config.mainWin.textbox.SendScintilla(QsciScintilla.SCI_GETCURRENTPOS))
    
    def mouseReleaseEvent(self, event):
        self.pressing = False
        # place the cursor back where it was
        config.mainWin.textbox.setFocus()
        config.mainWin.textbox.SendScintilla(QsciScintilla.SCI_SETCURSOR, self.position)

    def wheelEvent(self, event):
        # can't scroll on this one
        return
    
    def mouseDoubleClickEvent(self, event):
        return
