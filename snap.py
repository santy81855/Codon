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

class ButtonFormat(QPushButton):
    def __init__(self, parent):
        super(ButtonFormat, self).__init__()
        self.parent = parent
        self.setStyleSheet("""
        QPushButton
        {
            font-size: 18px;
            background-color: """+config.backgroundColor+""";
            color: """+config.backgroundColor+""";
            border-style: solid;
            border-width: 2px;
            border-radius: 10px;
            border-color: #8FBCBB;
        }
        QPushButton::hover
        {
            background-color:#8FBCBB;
        }
        """)
        self.setMouseTracking(True)
    
    def mouseMoveEvent(self, event):
        QApplication.setOverrideCursor(Qt.PointingHandCursor)

class SnapBox(QFrame):
    def __init__(self, parent):
        super(SnapBox, self).__init__()
        self.parent = parent
        self.setWindowFlags(Qt.FramelessWindowHint)
        # get the current geometry of the snap button
        #self.move(self.parent.mapToGlobal(self.parent.pos()))
        #self.setFixedSize(400, 200)
        
        self.setMouseTracking(True)
        self.setStyleSheet("""
        border-style:solid;
        border-width:3px;
        border-radius: 20px;
        border-color: #8FBCBB;
        background-color:"""+config.backgroundColor+""";
        """)
        # create the main horizoontal layout
        self.layout = QHBoxLayout()
        
        # create the 3 vertical layouts
        self.leftVert = QVBoxLayout()
        self.middleVert = QVBoxLayout()
        self.rightVert = QVBoxLayout()

        # create a max button
        self.max = ButtonFormat(self)
        self.max.setFixedSize(120, 140)
        self.max.setText("maximize")
        self.max.setStyleSheet("""
        QPushButton
        {
            font-size: 18px;
            background-color: """+config.backgroundColor+""";
            color: #8FBCBB;
            border:none;
            border-radius:10px;
        }
        QPushButton::hover
        {
            background-color:#8FBCBB;
            color:"""+config.backgroundColor+""";
        }
        """)
        self.max.clicked.connect(self.maxClicked)
        self.min = ButtonFormat(self)
        self.min.setFixedSize(120, 140)
        self.min.setText("minimize")
        self.min.setStyleSheet("""
        QPushButton
        {
            font-size: 18px;
            background-color: """+config.backgroundColor+""";
            color: #8FBCBB;
            border:none;
            border-radius:10px;
        }
        QPushButton::hover
        {
            background-color:#8FBCBB;
            color:"""+config.backgroundColor+""";
        }
        """)
        self.min.clicked.connect(self.minClicked)

        # add 2 buttons to the left one
        self.topleft = ButtonFormat(self)
        self.topleft.setText("top left")
        self.topleft.clicked.connect(self.tl)
        self.topleft.setFixedSize(120, 70)
        self.bottomleft = ButtonFormat(self)
        self.bottomleft.setText("bottom left")
        self.bottomleft.clicked.connect(self.bl)
        self.bottomleft.setFixedSize(120, 70)
        self.leftVert.addWidget(self.topleft)
        self.leftVert.addWidget(self.min)
        self.leftVert.addWidget(self.bottomleft)

        # add buttons to the middle
        self.top = ButtonFormat(self)
        self.top.setText("top")
        self.top.clicked.connect(self.topClicked)
        self.top.setFixedSize(360, 70)
        self.bottom = ButtonFormat(self)
        self.bottom.setText("bottom")
        self.bottom.clicked.connect(self.bottomClicked)
        self.bottom.setFixedSize(360, 70)
        self.left = ButtonFormat(self)
        self.left.setText("left")
        self.left.clicked.connect(self.leftClicked)
        self.left.setFixedSize(115, 140)
        self.middle = ButtonFormat(self)
        self.middle.setText("middle")
        self.middle.clicked.connect(self.middleClicked)
        self.middle.setFixedSize(115, 140)
        self.right = ButtonFormat(self)
        self.right.setText("right")
        self.right.clicked.connect(self.rightClicked)
        self.right.setFixedSize(115, 140)
        self.middlehorizontal = QHBoxLayout()
        self.middlehorizontal.addWidget(self.left)
        self.middlehorizontal.addWidget(self.middle)
        self.middlehorizontal.addWidget(self.right)
        self.middleVert.addWidget(self.top)
        self.middleVert.addLayout(self.middlehorizontal)
        self.middleVert.addWidget(self.bottom)

        # add buttons to the right
        self.topright = ButtonFormat(self)
        self.topright.setText("top right")
        self.topright.clicked.connect(self.tr)
        self.topright.setFixedSize(120, 70)
        self.bottomright = ButtonFormat(self)
        self.bottomright.setText("bottom right")
        self.bottomright.clicked.connect(self.br)
        self.bottomright.setFixedSize(120, 70)
        self.rightVert.addWidget(self.topright)
        self.rightVert.addWidget(self.max)
        self.rightVert.addWidget(self.bottomright)
        
        # add the left to the horizontal layout
        self.layout.addLayout(self.leftVert)
        self.layout.addLayout(self.middleVert)
        self.layout.addLayout(self.rightVert)
        
        self.setLayout(self.layout)
    
    def maxClicked(self):
        if config.isMaximized == False:
            self.parent.titlebarWidget.btn_max_clicked()
            self.hide()
            config.snapWidget = False
    
    def minClicked(self):
        self.parent.titlebarWidget.btn_min_clicked()
        self.hide()
        config.snapWidget = False

    def tl(self):
        config.upDown = True
        config.downDown = False
        config.leftDown = False
        config.rightDown = False
        self.parent.snapWin("left")
        self.hide()
        config.snapWidget = False
    
    def bl(self):
        config.downDown = False
        config.downDown = True
        config.leftDown = False
        config.rightDown = False
        self.parent.snapWin("left")
        self.hide()
        config.snapWidget = False

    def leftClicked(self):
        config.downDown = False
        config.upDown = False
        config.rightDown = False
        self.parent.snapWin("left")
        self.hide()
        config.snapWidget = False

    def rightClicked(self):
        config.downDown = False
        config.upDown = False
        config.leftDown = False
        self.parent.snapWin("right")
        self.hide()
        config.snapWidget = False
    
    def topClicked(self):
        config.rightDown = False
        config.leftDown = False
        config.upDown = False
        self.parent.snapWin("top")
        self.hide()
        config.snapWidget = False
    
    def bottomClicked(self):
        config.rightDown = False
        config.leftDown = False
        config.downDown = False
        self.parent.snapWin("bottom")
        self.hide()
        config.snapWidget = False
    
    def middleClicked(self):
        config.leftDown = True
        config.upDown = False
        config.downDown = False
        self.parent.snapWin("right")
        self.hide()
        config.snapWidget = False

    def tr(self):
        config.upDown = True
        config.downDown = False
        config.leftDown = False
        config.rightDown = False
        self.parent.snapWin("right")
        self.hide()
        config.snapWidget = False
    
    def br(self):
        config.upDown = False
        config.downDown = True
        config.leftDown = False
        config.rightDown = False
        self.parent.snapWin("right")
        self.hide()
        config.snapWidget = False
    
    def mouseMoveEvent(self, event):
        QApplication.setOverrideCursor(Qt.ArrowCursor)

        