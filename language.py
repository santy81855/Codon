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
from PyQt5.QtWidgets import QPushButton, QDesktopWidget, QComboBox
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
import config

class LanguageSelection(QComboBox):
    def __init__(self, parent):
        super(LanguageSelection, self).__init__()
        self.parent = parent
        self.addItems([
            "plain text", 
            "    python", 
            "         c", 
            "       cpp", 
            "        c#", 
            "      java", 
            "javascript", 
            "      json"])
        self.activated.connect(self.languageSelectionClicked)
        #self.setFixedSize(130, 30)
        self.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        #self.setMaximumSize(100, 20)
        
        self.setStyleSheet("""
            QComboBox::drop-down {border-width: 0px;}
            QComboBox::down-arrow {image:none; border-width: 0px;};
            selection-background-color: #5E81AC;
            background-color: #2E3440; 
            border:none;
            color: #8FBCBB;
            font: 12pt "Consolas";
            padding-left: 5px;
            padding-right: 5px;
            padding-top: 5px;
            padding-bottom: 5px;
            
                                """)
                                
        self.setMouseTracking(True)
    
    # if we select a different language syntax
    def languageSelectionClicked(self, index):
        language = self.itemText(index)
        self.setCurrentText(language)
        # since we put whitespaces in the name we have to remove them
        language = language.replace(" ", "")
        # if it is a language we support
        if language in config.languageDict:
            # update the tab's language
            config.tabArr[config.currentActiveTextBox].language = config.languageDict[language]
            # call the lexer for the textbox
            config.mainWin.textbox.getLexer()
            # call the lexer for the preview box
            config.mainWin.previewOverlay.previewbox.getLexer()
    
    def mouseMoveEvent(self, event):
        QApplication.setOverrideCursor(Qt.PointingHandCursor)
    
    def mousePressEvent(self, event):
        self.showPopup()
        config.mainWin.textbox.setFocus()
