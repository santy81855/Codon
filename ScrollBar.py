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

class ScrollBar(QScrollBar):
    def __init__(self, parent):
        super(ScrollBar, self).__init__()
        self.parent = parent
        self.setMouseTracking(True)
        self.setTracking(True)
        #self.setMinimumWidth(14)
        #self.setMaximumWidth(14)
        self.setStyleSheet("""
        QScrollBar::vertical
        {
            border:none;
            width: """ + str(config.scrollBarWidth) + """px;
        }
        QScrollBar::add-line:vertical
        {
            border:none;
            bagkground:none;
            width: 0px;
            height: 0px;
        }
        QScrollBar::sub-line:vertical
        {
            border:none;
            background:none;
            width: 0px;
            height: 0px;
        }
        QScrollBar::handle:vertical
        {
            background-color:"""+str(config.curLineColor)+"""; 
            border:none;  
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical 
        {
            background: none;
        }

                            """)
        #3B4252
    def mouseMoveEvent(self, event):
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        # call the normal mousemoveevent function so that we don't lose functionality
        QScrollBar.mouseMoveEvent(self, event)