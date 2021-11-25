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

class Overlay(QWidget):
    def __init__(self, parent):
        super(Overlay, self).__init__()
        self.previewbox = PreviewPane.TextPreview(parent)
        self.previewbox.setStyleSheet("""
            border: none;
                                """)
        self.previewbox.setGeometry(0, 0, 175, parent.height())
        previewFont = QFont()
        previewFont.setFamily("Consolas")
        previewFont.setFixedPitch( True )
        previewFont.setPointSize( 4 )
        self.previewbox.setFont( previewFont )
        #self.previewbox.resize(mainWin.width() / 3, mainWin.height() - 100)
        # you cannot type on it
        self.previewbox.setReadOnly(True)
        # don't be able to select it
        #self.previewbox.setTextInteractionFlags(Qt.NoTextInteraction)    
        # it can't get bigger than a certain width
        # make the width of the preview pane constant and about the same width as the min/max/close
        # corner buttons
        self.previewbox.setMaximumWidth(175)
        self.previewbox.setMinimumWidth(175)
        
        self.box = QPushButton(self)
        self.box.setText("hi")
        self.box.setStyleSheet("background-color: rgb(0,0,0,0);")
        self.box.setMinimumWidth(175)
        self.box.setMaximumWidth(175)
        self.box.setMinimumHeight(40)
        self.box.setMaximumHeight(40)
        self.box.setGeometry(0,0,175,40)
        