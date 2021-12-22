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
from PyQt5.QtWidgets import QWidget, QFrame
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

class ShortCutFormat(QPushButton):
    def __init__(self, parent, name):
        super(ShortCutFormat, self).__init__()
        self.parent = parent
        self.setText(name)
        # set the size of the widget
        width = config.mainWin.width()
        height = config.mainWin.height()
        self.setMaximumSize(width, height)
        self.setStyleSheet("""
        QPushButton
        {
            font-size: 20px;
            background-color: """+config.backgroundColor+""";
            color: #8FBCBB;
            border-style: solid;
            border-width: 1px;
            border-radius: 0px;
            border-color: #8FBCBB;
        }
        """)
        self.setMouseTracking(True)
        config.application.focusChanged.connect(self.on_focusChanged)
    
    def on_focusChanged(self, old, new):
        config.mainWin.textbox.setFocus()

    # get rid of the find menu when pressing escape
    def keyPressEvent(self, event):        
        config.mainWin.shortcutWidget.hide()

    def mousePressEvent(self, event):
        self.parent.hide()

    def mouseMoveEvent(self, event):
        QApplication.setOverrideCursor(Qt.ArrowCursor)

class ShortCuts(QFrame):
    def __init__(self, parent):
        super(ShortCuts, self).__init__()
        self.parent = parent
        self.setWindowFlags(Qt.FramelessWindowHint)
        # get the current geometry of the snap button
        #self.move(self.parent.mapToGlobal(self.parent.pos()))
        #self.setFixedSize(400, 200)
        
        self.setMouseTracking(True)
        self.setStyleSheet("""
        border-style:solid;
        border-width:3px;
        border-radius: 0px;
        border-color: #8FBCBB;
        background-color:"""+config.curLineColor+""";
        """)
        # create the horizontal layout
        self.layout = QHBoxLayout()
        self.layout.setSpacing(5)

        # create the title
        self.title = QLabel("s\nh\no\nr\nt\nc\nu\nt\ns")
        # Set the default font
        font = QFont()
        font.setFamily('Consolas')
        font.setWeight(QFont.Bold)
        font.setFixedPitch(True)
        font.setPointSize(config.fontSize+4)
        self.title.setFont(font)
        self.title.setStyleSheet("color:#8FBCBB;border:none;")
        self.title.setMaximumWidth(30)
        
        self.layout.addWidget(self.title)
        
        # create the 3 vertical layouts
        self.leftVert = QVBoxLayout()
        self.middleVert = QVBoxLayout()
        self.rightVert = QVBoxLayout()

        # add shortcuts to left middle and right intermittently
        self.newTab = ShortCutFormat(self, "New Tab:\nctrl+t")
        self.leftVert.addWidget(self.newTab)
        self.closeTab = ShortCutFormat(self, "Close Tab:\nctrl+w")
        self.middleVert.addWidget(self.closeTab)
        self.restoreTab = ShortCutFormat(self, "Restore Tab:\nctrl+r")
        self.rightVert.addWidget(self.restoreTab)
        self.openFile = ShortCutFormat(self, "Open File:\nctrl+o")
        self.leftVert.addWidget(self.openFile)
        self.saveFile = ShortCutFormat(self, "Save File:\nctrl+s")
        self.middleVert.addWidget(self.saveFile)
        self.saveFileAs = ShortCutFormat(self, "Save File As:\nctrl+shift+s")
        self.rightVert.addWidget(self.saveFileAs)
        self.jumpTab = ShortCutFormat(self, "Jump to Tab:\nctrl+number")
        self.leftVert.addWidget(self.jumpTab)
        self.nextTab = ShortCutFormat(self, "Next Tab:\nctrl+pgdn")
        self.middleVert.addWidget(self.nextTab)
        self.prevTab = ShortCutFormat(self, "Previous Tab:\nctrl+pgup")
        self.rightVert.addWidget(self.prevTab)
        self.snapWin = ShortCutFormat(self, "Snap:\nctrl+alt+arrow-key")
        self.leftVert.addWidget(self.snapWin)
        self.find = ShortCutFormat(self, "Find Dialogue:\nctrl+f")
        self.middleVert.addWidget(self.find)
        self.shortcutMenu = ShortCutFormat(self, "Shortcut Menu:\nctrl+h")
        self.rightVert.addWidget(self.shortcutMenu)
        # if i ever dont have the right amount of buttons, just make some with the same background as the main widget so that they are there but are invisible

        # add the left to the horizontal layout
        self.layout.addLayout(self.leftVert)
        self.layout.addLayout(self.middleVert)
        self.layout.addLayout(self.rightVert)
        
        self.setLayout(self.layout)
        config.application.focusChanged.connect(self.on_focusChanged)
    
    def on_focusChanged(self, old, new):
        config.mainWin.textbox.setFocus()

    def mouseMoveEvent(self, event):
        QApplication.setOverrideCursor(Qt.ArrowCursor)

    # get rid of the find menu when pressing escape
    def keyPressEvent(self, event):        
        config.mainWin.shortcutWidget.hide()

    def mousePressEvent(self, event):
        self.hide()
        