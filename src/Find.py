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
from PyQt5.Qsci import QsciScintilla
# to get the working monitor size
from win32api import GetMonitorInfo, MonitorFromPoint
import config

isRegex = False
isCaseSensitive = False
isWholeWord = False

class ReplaceBox(QPlainTextEdit):
    def __init__(self, parent):
        super(ReplaceBox, self).__init__()
        self.parent = parent
        # create the font
        font = QFont()
        font.setFamily('Consolas')
        font.setFixedPitch(True)
        font.setPointSize(config.fontSize)
        self.setPlaceholderText("Replace")
        self.setTabChangesFocus(True)
        self.setStyleSheet("""
        border:none;
        border-radius: 0px;
        background-color:"""+config.curLineColor+""";
        color:"""+config.textColor+""";
        selection-background-color:"""+config.selectionColor+""";
        selection-color:"""+config.selectionTextColor+""";
                                """)
        self.setFont(font)
        self.setLineWrapMode(0)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setMaximumSize(380,35)
        self.setMinimumSize(300,35)
        self.setMouseTracking(True)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            config.mainWin.isFind = False
            self.parent.hide()

        # if press enter on replace box then replace next
        elif event.key() == 16777220:
            self.parent.replaceNextClicked()

        else:
            # store the letter
            return QPlainTextEdit.keyPressEvent(self, event)
    
    def mouseMoveEvent(self, event):
        QApplication.setOverrideCursor(Qt.IBeamCursor)

class FindBox(QPlainTextEdit):
    def __init__(self, parent):
        super(FindBox, self).__init__()
        self.parent = parent
        # create the font
        font = QFont()
        font.setFamily('Consolas')
        font.setFixedPitch(True)
        font.setPointSize(config.fontSize)
        self.setPlaceholderText("Find")
        self.setStyleSheet("""
        border:none;
        border-radius: 0px;
        background-color:"""+config.curLineColor+""";
        color:"""+config.textColor+""";
        selection-background-color:"""+config.selectionColor+""";
        selection-color:"""+config.selectionTextColor+""";
                                """)
        self.setFont(font)
        self.setLineWrapMode(0)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setMaximumSize(380,35)
        self.setMinimumSize(300,35)
        self.setMouseTracking(True)
        self.isEnter = False

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            config.mainWin.isFind = False
            self.parent.hide()
        # if we press enter we need to move to the next instance
        elif event.key() == 16777220:
            if config.mainWin.textbox.hasSelectedText():
                config.mainWin.textbox.findNext()
                self.isEnter = True
        
        # if we press tab when on the find box we just move to the replace box
        elif event.text() == "\t":
            if self.parent.isReplace == False:
                self.parent.buttonClicked()

        else:
            self.isEnter = False
            # store the letter
            return QPlainTextEdit.keyPressEvent(self, event)
        
    def keyReleaseEvent(self, event):
        # want to update the replace and findtext as we type
        # search
        if self.isEnter == False:
            if config.mainWin.textbox.findFirst(self.toPlainText(), isRegex, isCaseSensitive, isWholeWord, True, True,
            0, 0, True, False) == False or self.toPlainText() == '':
                # place the cursor on the position of that tab
                config.mainWin.textbox.setCursorPosition(config.tabArr[config.currentActiveTextBox].curPos[0],
            config.tabArr[config.currentActiveTextBox].curPos[1])     
    
    def mouseMoveEvent(self, event):
        QApplication.setOverrideCursor(Qt.IBeamCursor)

class ButtonFormat(QPushButton):
    def __init__(self, parent, title):
        super(ButtonFormat, self).__init__()
        # create the font
        font = QFont()
        font.setFamily('Consolas')
        font.setFixedPitch(True)
        if title == "<" or title == ">":
            font.setPointSize(config.fontSize)    
        else:
            font.setPointSize(config.fontSize - 4)
        self.setText(title)
        self.setFont(font)
        self.setFixedSize(30,35)
        self.setStyleSheet("""
        QPushButton
        {
            color:"""+config.textColor+""";
            border:none;
            border-radius: 0px;
        }
        QPushButton::hover
        {
            background-color:"""+config.curLineColor+""";
        }
        
                                    """)
        self.setMouseTracking(True)
    
    def mouseMoveEvent(self, event):
        QApplication.setOverrideCursor(Qt.PointingHandCursor)

class FindWindow(QWidget):
    def __init__(self, parent):
        super(FindWindow, self).__init__()
        self.setMaximumHeight(50)
        # set the style for the widget
        self.setStyleSheet("""
        background-color:""" + config.backgroundColor + """
                        """)
        self.parent = parent
        # create the font
        font = QFont()
        font.setFamily('Consolas')
        font.setFixedPitch(True)
        font.setPointSize(config.fontSize)
        # create the main vertical layout
        self.findlayout = QVBoxLayout()
        # create the two horizontal layouts
        self.toprow = QHBoxLayout()
        self.bottomrow = QHBoxLayout()
        # create a vertical layout to store the replace toggle button in
        self.buttonvert = QVBoxLayout()
        # create a horizontal layout to store the buttons in 
        self.nextprevHor = QHBoxLayout()
        # create a vertical layout to store the button layout in
        self.nextprevVert = QVBoxLayout()
        # create a button that will be used to toggle the replacebox
        self.button = QPushButton(">")
        self.button.setStyleSheet("""
        QPushButton
        {
            color:"""+config.textColor+""";
            border:none;
            border-radius: 0px;
        }
        QPushButton::hover
        {
            background-color:"""+config.curLineColor+""";
        }
        
                                    """)
        self.button.setFont(font)
        self.button.setFixedSize(30,40)
        self.button.clicked.connect(self.buttonClicked)
        # create one more horizontal layout that will put the button on the left of toprow AND bottomrow
        self.horlayout = QHBoxLayout()
        self.buttonvert.addWidget(self.button)
        self.horlayout.addLayout(self.buttonvert)
        # create the find textbox
        self.find = FindBox(self)
        # add it to the toprow horizontal layout
        self.toprow.addWidget(self.find)
        # add a button to the top row for next and prev
        self.prev = ButtonFormat(self, "<")
        self.prev.clicked.connect(self.prevClicked)
        self.next = ButtonFormat(self, ">")
        self.next.clicked.connect(self.nextClicked)
        self.nextprevHor.addWidget(self.prev)
        self.nextprevHor.addWidget(self.next)
        self.nextprevVert.addLayout(self.nextprevHor)
        # create the replace text box
        self.replace = ReplaceBox(self)
        # add the replace box to the bottom horizontal layout
        self.bottomrow.addWidget(self.replace)
        # create buttons for case sensitive or whole word or regex
        self.caseSensitive = ButtonFormat(self, "Aa")
        self.caseSensitive.clicked.connect(self.caseSensitiveClicked)
        self.wholeWord = ButtonFormat(self, "|aa|")
        self.wholeWord.clicked.connect(self.wholeWordClicked)
        self.regex = ButtonFormat(self, "Re*")
        self.regex.clicked.connect(self.regexClicked)
        # create the replace next and replace all buttons
        self.replaceNext = ButtonFormat(self, "R")
        self.replaceNext.clicked.connect(self.replaceNextClicked)
        self.replaceAll = ButtonFormat(self, "RA")
        self.replaceAll.clicked.connect(self.replaceAllClicked)
        # add the buttons to the bottom row
        self.bottomrow.addWidget(self.replaceNext)
        self.bottomrow.addWidget(self.replaceAll)
        self.bottomrow.addStretch(1)
        # hide them by default
        self.replaceNext.hide()
        self.replaceAll.hide()
        # add all the top row buttons
        self.toprow.addWidget(self.caseSensitive)
        self.toprow.addWidget(self.wholeWord)
        self.toprow.addWidget(self.regex)
        # add the two horizontal layouts to the vertical layout
        self.findlayout.addLayout(self.toprow, 50)
        self.findlayout.addLayout(self.bottomrow, 50)
        self.horlayout.addLayout(self.findlayout)
        self.horlayout.addLayout(self.nextprevVert)
        self.setLayout(self.horlayout)
        self.replace.hide()
        self.setMouseTracking(True)
        self.isReplace = False
        self.findText = ""
        self.replaceText = ""
        self.forward = True

    def replaceNextClicked(self):
        if config.mainWin.textbox.hasSelectedText() == True:
            config.mainWin.textbox.replace(self.replace.toPlainText())
            if config.mainWin.textbox.findFirst(self.find.toPlainText(), isRegex, isCaseSensitive, isWholeWord, True, True,
            0, 0, True, False) == False or self.find.toPlainText() == "":
                # place the cursor on the position of that tab
                config.mainWin.textbox.setCursorPosition(config.tabArr[config.currentActiveTextBox].curPos[0],
        config.tabArr[config.currentActiveTextBox].curPos[1])    
    
    def replaceAllClicked(self):
        cur = config.mainWin.textbox.getCursorPosition()
        line = cur[0]
        col = cur[1]
        num = 0

        while config.mainWin.textbox.hasSelectedText() == True and self.find.toPlainText() != "":
            config.mainWin.textbox.replace(self.replace.toPlainText())
            if config.mainWin.textbox.hasSelectedText() == True and self.find.toPlainText() in self.replace.toPlainText():
                # make sure that we don't repeat steps
                tempCur = config.mainWin.textbox.getCursorPosition()
                tempLine = tempCur[0]
                tempCol = tempCur[1]
                # get the length of the word - the length of the substring
                diff = len(self.replace.toPlainText()) - len(self.find.toPlainText())
                if tempLine == line and tempCol - diff == col and num > 0:
                    # replace the last replacement with the find text since this method does 1 replacement too many
                    config.mainWin.textbox.findFirst(self.replace.toPlainText(), isRegex, isCaseSensitive,
                    isWholeWord, True, True, 0, 0, True, False)
                    config.mainWin.textbox.replace(self.find.toPlainText())
                    break
                num += 1
                config.mainWin.textbox.findNext()                
            else: 
                if config.mainWin.textbox.findFirst(self.find.toPlainText(), isRegex, isCaseSensitive,
        isWholeWord, True, True, 0, 0, True, False) == False or self.find.toPlainText() == "":
                    break
                
        config.mainWin.textbox.setCursorPosition(config.tabArr[config.currentActiveTextBox].curPos[0],
        config.tabArr[config.currentActiveTextBox].curPos[1])    
    
    
    def wholeWordClicked(self):
        global isWholeWord
        if isWholeWord == False:
            isWholeWord = True
            self.wholeWord.setStyleSheet("""
            QPushButton
            {
                background-color:"""+config.backgroundColor+""";
                color:#8FBCBB;
                border:none;
                border-radius: 0px;
            }
            QPushButton::hover
            {
                background-color:#8FBCBB;
                color:"""+config.backgroundColor+""";
            }
            """)
        else:
            isWholeWord = False
            self.wholeWord.setStyleSheet("""
            QPushButton
            {
                color:"""+config.textColor+""";
                border:none;
                border-radius: 0px;
            }
            QPushButton::hover
            {
                background-color:"""+config.curLineColor+""";
            }
            """)
    
    def regexClicked(self):
        global isRegex
        if isRegex == False:
            isRegex = True
            self.regex.setStyleSheet("""
            QPushButton
            {
                background-color:"""+config.backgroundColor+""";
                color:#8FBCBB;
                border:none;
                border-radius: 0px;
            }
            QPushButton::hover
            {
                background-color:#8FBCBB;
                color:"""+config.backgroundColor+""";
            }
            """)
        else:
            isRegex = False
            self.regex.setStyleSheet("""
            QPushButton
            {
                color:"""+config.textColor+""";
                border:none;
                border-radius: 0px;
            }
            QPushButton::hover
            {
                background-color:"""+config.curLineColor+""";
            }
            """)
    
    def caseSensitiveClicked(self):
        global isCaseSensitive
        if isCaseSensitive == False:
            isCaseSensitive = True
            self.caseSensitive.setStyleSheet("""
            QPushButton
            {
                background-color:"""+config.backgroundColor+""";
                color:#8FBCBB;
                border:none;
                border-radius: 0px;
            }
            QPushButton::hover
            {
                background-color:#8FBCBB;
                color:"""+config.backgroundColor+""";
            }
            """)
        else:
            isCaseSensitive = False
            self.caseSensitive.setStyleSheet("""
            QPushButton
            {
                color:"""+config.textColor+""";
                border:none;
                border-radius: 0px;
            }
            QPushButton::hover
            {
                background-color:"""+config.curLineColor+""";
            }
            """)

    def nextClicked(self):
        if config.mainWin.textbox.hasSelectedText():
            # if we are currently moving backward then we want to swap directions
            if self.forward == False:
                # get the current cursor position on the toxbox
                pos = config.mainWin.textbox.getCursorPosition()
                # get the length of the selected word
                x = len(config.mainWin.textbox.selectedText())
                # find first from beginning of word, so it should reselect itself, but forward this time
                config.mainWin.textbox.findFirst(self.find.toPlainText(), False, False, False, True, True,
                pos[0], pos[1] - x, True, False)
                self.forward = True
                config.mainWin.textbox.findNext()
            else:
                config.mainWin.textbox.findNext()
    
    def prevClicked(self):
        if config.mainWin.textbox.hasSelectedText():
            if self.forward == True:
                config.mainWin.textbox.findFirst(self.find.toPlainText(), False, False, False, True, False,
                -1, -1, True, False)
                self.forward = False
                config.mainWin.textbox.findNext()
            else:
                config.mainWin.textbox.findNext()

    def buttonClicked(self):
        # if replace box is not up we add it
        if self.isReplace == False:
            self.setMaximumHeight(100)
            self.replace.show()
            self.replaceNext.show()
            self.replaceAll.show()
            self.button.setFixedSize(30,80)
            self.prev.setFixedSize(30,80)
            self.next.setFixedSize(30,80)
            self.isReplace = True
            self.activateWindow()
            self.replace.setFocus(True)
        else:
            self.hide()
            self.setMaximumHeight(50)
            self.parent.isFind = False
            self.parent.showFind()

    def mouseMoveEvent(self, event):
        QApplication.setOverrideCursor(Qt.ArrowCursor)