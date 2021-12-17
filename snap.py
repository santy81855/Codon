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

class SnapBox(QWidget):
    def __init__(self, parent):
        super(SnapBox, self).__init__()
        self.parent = parent
        self.setWindowFlags(Qt.FramelessWindowHint)
        # get the current geometry of the snap button
        buttonGeometry = self.parent.snapButton.geometry()
        #print(buttonGeometry)
        x = buttonGeometry.x()
        y = buttonGeometry.y()
        point = self.mapToGlobal(self.parent.snapButton.pos())
        #self.setFixedSize(400, 200)
        self.setGeometry(point.x(), point.y(), 400, 200)
        
        self.setMouseTracking(True)
        self.setStyleSheet("""
        border:none;
        background-color:"""+config.backgroundColor+""";
        """)