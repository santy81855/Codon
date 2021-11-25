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
import TitleBar, Tab, WordCount, PreviewPane, TextBox, main
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

class Tab(QWidget):
    def __init__(self, fileName, filePath, contents):
        super(Tab, self).__init__()
        global usedNums
        self.fileName = ""
        self.fileLocation = ""
        if fileName == "":
            numToUse = -1
            for i in range(1, 1000):
                if config.usedNums[i] == False:
                    numToUse = i
                    config.usedNums[i] = True
                    break
            self.fileName = "untitled_" + str(numToUse) + ".txt"
        else:
            self.fileName = fileName
        # add the file path
        if filePath == "":
            self.filePath = ""
        else:
            self.filePath = filePath
        # variable to check if it is up to date
        self.isSaved = False
        # variable to store the language of the file(code)
        self.language = self.getFileType()
        # variable to store the contents of the text box
        self.contents = contents
        # variable to store the word count of the document
        self.wordCount = 0
        # cursor position
        self.curPos = (0,0)
        # set the word count on the button if there is any content to this file
        if contents != "":
            # use regex to split it into a list of words
            text = re.findall('[\w\-]+', contents)
            # update the variable storing the wordcount of the tab to be the length of the list we
            # just got
            self.wordCount = len(text)
            # update the value of the word count button
            #mainWin.infobarlayout.itemAt(wordCountIndex).widget().setText(str(self.wordCount))
        # create a layout that can store the tab and its close button
        self.singleTabLayout = QHBoxLayout()
        # create a button to represent the file
        self.tabButton = QPushButton(self.fileName)
        self.tabButton.setMouseTracking(True)
        self.tabButton.clicked.connect(self.tabClicked)
        self.tabButton.setMinimumSize(200, 40)
        self.tabButton.adjustSize()
        self.tabButton.setStyleSheet("""
            QPushButton
            {
            background-color: #2E3440;
            color: #D8DEE9;
            font: 14pt "Consolas";
            border: none;
            padding: 10px;
            }
            QPushButton::hover
            {
            background-color: #4C566A;
            color: #D8DEE9;
            border: none;
            padding: 10px;
            }  
                                    """)
        # install event filter on the button so we can detect right click
        self.tabButton.installEventFilter(self)
        self.setMouseTracking(True)
        self.singleTabLayout.addWidget(self.tabButton)
        #------------------------------------------------------------------------------------------------
        # create a smaller button for closing the tab that is normally the same color as the tab
        # but will turn red if hovered
        self.closeButton = QPushButton("")
        self.closeButton.setMouseTracking(True)
        #self.closeButton.clicked.connect(self.tabClose)
        self.closeButton.setMinimumSize(20, 40)
        self.closeButton.adjustSize()
        self.closeButton.setStyleSheet("""
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
        #self.singleTabLayout.addWidget(self.closeButton)
        #-----------------------------------------------------------------------------------------------
        self.setLayout(self.singleTabLayout)
        # left, top, right, bottom
        self.singleTabLayout.setContentsMargins(0,0,0,0)        
        self.tabClicked()
        
    # function to get the filetype of the current tab
    def getFileType(self):
        name = self.fileName
        if ".py" in name:
            return "py"
        elif ".c" in name:
            return "c"
        elif ".java" in name:
            return "java"
        elif ".cpp" in name:
            return "cpp"
        elif ".js" in name:
            return "js"
        elif ".cs" in name:
            return "cs"
        elif ".json" in name:
            return "json"
        else:
            return "plaintext"
    
    # event filter to detect right click
    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            # if we right click we want to remove that tab
            if event.button() == QtCore.Qt.RightButton:
                # get the index of the tab we want to close
                tabIndex = -1
                for tab in config.tabArr:
                    if tab == self:
                        config.tabIndex = config.tabArr.index(tab)
                        break
                config.mainWin.closeTab(config.tabIndex, config.currentActiveTextBox)
        return QtCore.QObject.event(obj, event)
    
    # when hovering over a tab it should be the little hand cursor
    def mouseMoveEvent(self, event):
        QApplication.setOverrideCursor(Qt.PointingHandCursor)

    def tabClicked(self):
        # when we click the tab, we want to focus the tab by changing its color to be the same as
        # the background
        self.tabButton.setStyleSheet("""
            QPushButton
            {
            background-color: #8FBCBB;
            color: #2E3440;
            font: 14pt "Consolas";
            border: none;
            padding: 10px;
            }
            QPushButton::hover
            {
            background-color: #8FBCBB;
            color: #4C566A;
            border: none;
            padding: 10px;
            }-  
                                    """)
        # Go to the contents of the tab that was clicked
        for i in range(0, len(config.tabArr)):
            # if we find the right tab we know which textbox to display
            if config.tabArr[i] == self:
                config.mainWin.displayTextBox(i)
            # if it's not the right tab then color it in the unfocused color
            else:
                config.tabArr[i].tabButton.setStyleSheet("""
            QPushButton
            {
            background-color: #2E3440;
            color: #D8DEE9;
            font: 14pt "Consolas";
            border: none;
            padding: 10px;
            }
            QPushButton::hover
            {
            background-color: #4C566A;
            color: #D8DEE9;
            border: none;
            padding: 10px;
            }-  
                                    """)
        # change the title of the window to be the tab name
        #config.mainWin.layout.itemAt(0).widget().title.setText(self.fileName + " - notepad")
   