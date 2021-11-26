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

class FindWindow(QWidget):
    def __init__(self, parent):
        super(FindWindow, self).__init__()
        # set the style for the widget
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("""
        border:none;
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
        # create a vertical layout to store the button in
        self.buttonvert = QVBoxLayout()
        # create a button that will be used to toggle the replacebox
        self.button = QPushButton(">")
        self.button.setStyleSheet("""
        color:"""+config.textColor+""";
        border:none;
                                    """)
        self.button.setFont(font)
        self.button.setFixedSize(30,40)
        self.button.clicked.connect(self.buttonClicked)
        # create one more horizontal layout that will put the button on the left of toprow AND bottomrow
        self.horlayout = QHBoxLayout()
        self.buttonvert.addWidget(self.button)
        self.horlayout.addLayout(self.buttonvert)
        # create the find textbox
        self.find = QPlainTextEdit("")
        self.find.setPlaceholderText("Find")
        self.find.setTabChangesFocus(True)
        self.find.setStyleSheet("""
        border:none;
        background-color:"""+config.curLineColor+""";
        color:"""+config.textColor+""";
                                """)
        self.find.setFont(font)
        self.find.setLineWrapMode(0)
        self.find.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.find.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.find.setMaximumSize(300,35)
        # add it to the toprow horizontal layout
        self.toprow.addWidget(self.find)
        # create the replace text box
        self.replace = QPlainTextEdit()
        self.replace.setPlaceholderText("Replace")
        self.replace.setTabChangesFocus(True)
        self.replace.setStyleSheet("""
        border: none;
        background-color:"""+config.curLineColor+""";
        color:"""+config.textColor+""";
                                """)
        self.replace.setFont(font)
        self.replace.setLineWrapMode(0)
        self.replace.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.replace.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.replace.setMaximumSize(300,35)
        # add the replace box to the bottom horizontal layout
        self.bottomrow.addWidget(self.replace)
        # add the two horizontal layouts to the vertical layout
        self.findlayout.addLayout(self.toprow, 50)
        self.findlayout.addLayout(self.bottomrow, 50)
        self.horlayout.addLayout(self.findlayout)
        self.setLayout(self.horlayout)
        self.replace.hide()
        self.setMouseTracking(True)
        self.isReplace = False

    def buttonClicked(self):
        # if replace box is not up we add it
        if self.isReplace == False:
            self.replace.show()
            self.button.setFixedSize(30,80)
            self.isReplace = True
        else:
            self.replace.hide()
            self.button.setFixedSize(30,35)
            self.buttonvert.addStretch(1)
            self.isReplace = False
        
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            config.mainWin.isFind = False
            self.hide()
        else:
            return QWidget.keyPressEvent(self, event)    

    def mouseMoveEvent(self, event):
        QApplication.setOverrideCursor(Qt.ArrowCursor)