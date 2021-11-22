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

class WordCountButton(QPushButton):
    def __init__(self, parent):
        super(WordCountButton, self).__init__()
        self.parent = parent
        self.setText("wc:113")
        self.clicked.connect(self.wordCountClicked)
        #self.setFixedSize(20, 20)
        self.adjustSize()
        #self.setMaximumSize(100, 20)
        self.setStyleSheet("""
            QPushButton
            {
            background-color: #2E3440; 
            border:none;
            color: #8FBCBB;
            font: 12pt "Consolas";
            padding-left: 5px;
            padding-right: 5px;
            padding-top: 5px;
            padding-bottom: 5px;
            }
                                """)
                                
        self.setMouseTracking(True)
    
    def wordCountClicked(self):
        print("here")
