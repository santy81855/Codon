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
import config
# to get the working monitor size
from win32api import GetMonitorInfo, MonitorFromPoint

class SnapButton(QPushButton):
    def __init__(self, parent):
        super(SnapButton, self).__init__()
        self.parent = parent
        self.setText("snap")
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

    # when we hover over this widget should show but disappear when we unhover
    def mouseMoveEvent(self, event):
        QApplication.setOverrideCursor(Qt.PointingHandCursor)
        if config.isSnapWidget == False:
            mainPosition = self.parent.mapToGlobal(QPoint(0,self.parent.height()))
            config.mainWin.snapWidget.setGeometry(mainPosition.x() + self.parent.width() / 2 - 315, mainPosition.y() - 380, 600, 300)
            self.parent.snapWidget.show()
            config.isSnapWidget = True
        
