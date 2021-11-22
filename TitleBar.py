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
import TitleBar, Tab, WordCount, PreviewPane, TextBox, main
import config

class MyBar(QWidget):
    def __init__(self, parent):
        super(MyBar, self).__init__()
        global titleBar
        btn_size = 35
        titleBar = self
        # make the main window the parent
        self.parent = parent
        # create the layout to store the titlebar and buttons horizontally
        self.layout = QHBoxLayout()
        # allow for 8 pixels at the right so we can resize right and top right
        # also 8 margin at the top so that the buttons don't get in the way of resizing
        # left, top, right, bottom
        # add left margin to account for 3 corner buttons so the title is centered
        self.layout.setContentsMargins(btn_size*3,0,0,0)
        self.layout.setSpacing(0)
        self.title = QLabel("notes app")
        self.title.setMouseTracking(True)

        self.btn_close = QPushButton("x")
        self.btn_close.clicked.connect(self.btn_close_clicked)
        # make the corner buttons more rectangular in the horizontal way
        self.btn_close.setFixedSize(btn_size+25,btn_size)
        self.btn_close.setStyleSheet("""
            QPushButton
            {
            background-color: #2E3440; 
            border:none;
            color: #E5E9F0;
            font: 14pt "Consolas";
            }
            QPushButton::hover
            {
                background-color : #990000;
            }
                                """)
        self.btn_close.setMouseTracking(True)

        self.btn_min = QPushButton("-")
        self.btn_min.clicked.connect(self.btn_min_clicked)
        self.btn_min.setFixedSize(btn_size+25, btn_size)
        self.btn_min.setStyleSheet("""
            QPushButton
            {
            background-color: #2E3440; 
            border:none;
            color: #E5E9F0;
            font: 14pt "Consolas";
            }
            QPushButton::hover
            {
                background-color : #D8DEE9;
                color: #2E3440;
            }
                                """)
        self.btn_min.setMouseTracking(True)
        self.btn_max = QPushButton("+")
        self.btn_max.clicked.connect(self.btn_max_clicked)
        self.btn_max.setFixedSize(btn_size+25, btn_size)
        self.btn_max.setStyleSheet("""
            QPushButton
            {
            background-color: #2E3440; 
            border:none;
            color: #E5E9F0;
            font: 14pt "Consolas";
            }
            QPushButton::hover
            {
                background-color : #D8DEE9;
                color: #2E3440;
            }
                                """)
        self.btn_max.setMouseTracking(True)
        # give the title bar a height
        self.title.setFixedHeight(btn_size)
        self.title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.btn_min)
        self.layout.addWidget(self.btn_max)
        self.layout.addWidget(self.btn_close)

        self.title.setStyleSheet("""
            background-color: #2E3440;
            color: #8FBCBB;
            font: 14pt "Consolas";
            """)
        self.setLayout(self.layout)

        self.start = QPoint(0, 0)
        # flags for resizing or dragging window
        self.pressing = False
        self.movingPosition = False
        self.resizingWindow = False
        self.setMouseTracking(True)
        # flags for starting location of resizing window
        self.left = False
        self.right = False
        self.top = False
        self.tl = False
        self.tr = False
    
    # close the main window when the close button in the menu bar is pressed
    def btn_close_clicked(self):
        # if there are more than 1 tab open
        if len(config.tabArr) > 1:
            msg = QMessageBox()
            msg.setWindowTitle("Notes")
            msg.setText("Do you want to close all of the tabs?")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
            msg.setDefaultButton(QMessageBox.Yes)
            msg.setIcon(QMessageBox.Question)
            # cancel = 4194304
            # else yes
            QApplication.setOverrideCursor(Qt.ArrowCursor)
            ans = msg.exec_()
            # if yes
            if ans != 4194304:
                self.parent.close()
        # if there is 1 tab and it is not saved then just bring up the closeTab dialogue
        elif len(config.tabArr) == 1 and config.tabArr[0].isSaved == False:
            self.parent.closeTab(0, 0)
        # otherwise just close
        else:
            self.parent.close()

    def btn_max_clicked(self):
        global isMaximized

        # if it is clicked while we are currently maximized, then it means we need to revert to
        # lastPosition
        if config.isMaximized:
            self.parent.showNormal()
            config.isMaximized = False
        # if it is not maximized
        else:
            # if the maximize button is pressed on the menubar, it should call the maximize function of
            # the parent window. It is a standard function, so it is not written in this code
            self.parent.showMaximized()
            # toggle isMax so we know the state
            config.isMaximized = True
        # focus on the textbox
        #self.parent.layout.itemAt(textBoxIndex).widget().setFocus()
        self.parent.layout.itemAt(config.textBoxIndex).itemAt(0).widget().setFocus()

    def btn_min_clicked(self):
        # same with the show minimized
        self.parent.showMinimized()
    
    def mouseDoubleClickEvent(self, event):
        # only a left double click will max and restore
        if event.button() == 1:
            self.btn_max_clicked()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            return
        pos = event.pos()
        self.pressing = True
        if config.isMaximized == False:
            self.movingPosition = True
            self.start = self.mapToGlobal(event.pos())

    def mouseMoveEvent(self, event):
        pos = event.pos()
        # top left
        if pos.x() <= 3 and pos.y() <= 3:
            QApplication.setOverrideCursor(Qt.SizeFDiagCursor)
        
        else:
            QApplication.setOverrideCursor(Qt.ArrowCursor)
        if config.isMaximized == False:
            # moving the window
            if self.pressing and self.movingPosition:
                self.end = self.mapToGlobal(event.pos())
                self.movement = self.end-self.start
                self.parent.setGeometry(self.mapToGlobal(self.movement).x() - 5,
                                    self.mapToGlobal(self.movement).y() - 5,
                                    self.parent.width(),
                                    self.parent.height())
                self.start = self.end

    def mouseReleaseEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.RightButton:
            return
        self.pressing = False
        self.movingPosition = False
