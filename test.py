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

class QLineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.codeEditor = editor
        self.setMouseTracking(True)
    
    def mouseMoveEvent(self, event):
        QApplication.setOverrideCursor(Qt.ArrowCursor)

    def sizeHint(self):
        return QSize(self.editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.codeEditor.lineNumberAreaPaintEvent(event)


class QCodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lineNumberArea = QLineNumberArea(self)
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.updateLineNumberAreaWidth(0)
        self.setMouseTracking(True)
        self.startCursorPosition = 0
        self.endCursorPosition = 0
        self.oldPosition = 0
        self.is_first_input = False
    
    def keyPressEvent(self, event):
        global wordCount
        # no matter what we want to update the preview pane
        mainWin.layout.itemAt(textBoxIndex).itemAt(1).widget().setPlainText(mainWin.layout.itemAt(textBoxIndex).itemAt(0).widget().toPlainText())
        # if we press back tab (shift + tab)
        if event.key() == QtCore.Qt.Key_Backtab:
            # get current cursor
            cur = self.textCursor()
            # check if there is anything selected
            if cur.hasSelection() == True:
                # store the anchor and position of the cursor
                oldAnchor = cur.anchor()
                oldPos = cur.position()
                cur.movePosition(QTextCursor.StartOfLine)
                startofline = cur.position()
                
                # move the cursor so that it is selecting from the beginning of the first line
                # move it to the start of the line before you clear the selection
                cur.clearSelection()
                cur.setPosition(oldAnchor, QTextCursor.MoveAnchor)
                cur.setPosition(startofline, QTextCursor.KeepAnchor)
                # store the selected text with the new info
                text = cur.selection().toPlainText()
                # split the text up into lines at every new line
                lines = text.split('\n')
                # add a newline and a tab at the front of each line since we removed the newlines
                # with the split command above
                # offset just tracks if we removed any tabs or not
                offset = 0
                for line in lines:
                    if lines.index(line) == 0:
                        if '\t' in line: 
                            line = line[1:]
                            offset = 1
                        cur.insertText(line) 
                    else:
                        if '\t' not in line:
                            line = '\n' + line
                        else:
                            line = '\n' + line[1:]
                            offset = 1
                        cur.insertText(line)
                        
                # reselect the same text that was selected to begin with
                if oldAnchor < oldPos:
                    newAnchor = oldAnchor
                    newPos = cur.position()
                else:
                    newAnchor = cur.position()
                    newPos = oldPos
                cur.setPosition(newAnchor, QTextCursor.MoveAnchor)
                cur.setPosition(newPos - offset, QTextCursor.KeepAnchor)
                self.setTextCursor(cur)
            # if nothing is selected we just want to backtab the current line
            else:
                # store the position of the cursor
                position = cur.position()
                # move it to the front of the line
                cur.movePosition(QTextCursor.StartOfLine)
                # select the very first character in the line
                cur.setPosition(cur.position(), QTextCursor.MoveAnchor)
                cur.setPosition(cur.position() + 1, QTextCursor.KeepAnchor)
                # if the first character is a tab then we want to remove that tab
                if cur.selectedText() == '\t':
                    cur.removeSelectedText()
                # and move the cursor back to where it was
                cur.movePosition(position)
        # if we press enter
        elif event.key() == 16777220:
            # get current cursor
            cur = self.textCursor()
            initialposition = cur.position()
            # select the character right before the text cursor
            char = 'f'
            if cur.position() > 0:
                cur.setPosition(cur.position(), QTextCursor.MoveAnchor)
                cur.setPosition(cur.position() - 1, QTextCursor.KeepAnchor)
                char = cur.selectedText()
            # if the selected character is an opening curly bracket then we insert a newline and
            # 1 more tab than the line we were just on
            if char == '{':
                cur.clearSelection()
                cur.setPosition(initialposition, QTextCursor.MoveAnchor)
                cur.insertText('\n' + '\t')
                initialposition += 2
                # now check if the item to the right of the cursor is a closing bracket
                cur.setPosition(cur.position(), QTextCursor.MoveAnchor)
                cur.setPosition(cur.position() + 1, QTextCursor.KeepAnchor)
                if cur.selectedText() == '}':
                    # we just want to move it to the next line
                    cur.setPosition(initialposition, QTextCursor.MoveAnchor)
                    newposition = cur.position()
                    cur.insertText('\n')
                    cur.movePosition(newposition - 1)
                    self.setTextCursor(cur)
            else:
                return QPlainTextEdit.keyPressEvent(self, event)
        
        # when we press tab 
        elif event.key() == QtCore.Qt.Key_Tab:
            # get current cursor
            cur = self.textCursor()
            # check if there is anything selected
            if cur.hasSelection() == True:
                # store the anchor and position of the cursor
                oldAnchor = cur.anchor()
                oldPos = cur.position()
                cur.movePosition(QTextCursor.StartOfLine)
                startofline = cur.position()
                
                # move the cursor so that it is selecting from the beginning of the first line
                # move it to the start of the line before you clear the selection
                #cur.movePosition(oldAnchor)
                cur.clearSelection()
                cur.setPosition(oldAnchor, QTextCursor.MoveAnchor)
                cur.setPosition(startofline, QTextCursor.KeepAnchor)
                # store the selected text with the new info
                text = cur.selection().toPlainText()
                # split the text up into lines at every new line
                lines = text.split('\n')
                # add a newline and a tab at the front of each line since we removed the newlines
                # with the split command above
                for line in lines:
                    if lines.index(line) > 0:
                        line = '\n\t' + line
                    else:
                        line = '\t' + line
                    cur.insertText(line)
                # reselect the same text that was selected to begin with
                if oldAnchor < oldPos:
                    newAnchor = oldAnchor
                    newPos = cur.position()
                else:
                    newAnchor = cur.position()
                    newPos = oldPos
                cur.setPosition(newAnchor, QTextCursor.MoveAnchor)
                cur.setPosition(newPos + 1, QTextCursor.KeepAnchor)
                self.setTextCursor(cur)
                
            else:
                # store the position of the cursor
                position = cur.position()
                # move it to the front of the line
                cur.movePosition(QTextCursor.StartOfLine)
                # insert the tab
                cur.insertText('\t')
                # and move it back to where it was
                cur.movePosition(position)
        else:
            # any time we type a letter update the word count (this probably does not scale well)
            # get the text of this tabs textbox
            # add the current key as well to account for the first letter being pressed
            text = str(event.text()) + tabArr[currentActiveTextBox].contents
            # if we just pasted then we want to get the most updated contents of the textbox
            if event.matches(QKeySequence.Paste):
                text = text + QApplication.clipboard().text()
            # remove the last letter of the text if it is a backspace
            if event.key() == QtCore.Qt.Key_Backspace:
                # in case we are deleting more than a single character through selection
                cur = self.textCursor()
                if cur.hasSelection() == True:
                    selectedText = cur.selectedText()
                    text = text.replace(selectedText, "")
                else:
                    text = text[:-1]
            # use regex to split it into a list of words
            text = re.findall('[\w\-]+', text)
            # update the variable storing the wordcount of the tab to be the length of the list we
            # just got
            tabArr[currentActiveTextBox].wordCount = len(text)
            # update the value of the word count button
            mainWin.infobarlayout.itemAt(wordCountIndex).widget().setText(str(tabArr[currentActiveTextBox].wordCount))
            return QPlainTextEdit.keyPressEvent(self, event)
    
    def mouseMoveEvent(self, event):
        QApplication.setOverrideCursor(Qt.IBeamCursor)
        # call the normal mousemoveevent function so that we don't lose functionality
        QPlainTextEdit.mouseMoveEvent(self, event)
            
    def lineNumberAreaWidth(self):
        # since we just added a new line we need to place an enter key on the previewtextbox
        if mainWin.layout.itemAt(textBoxIndex) is not None:
            text = mainWin.layout.itemAt(textBoxIndex).itemAt(1).widget().toPlainText()
            mainWin.layout.itemAt(textBoxIndex).itemAt(1).widget().setPlainText(text + '\n')
        digits = 1
        max_value = max(1, self.blockCount())
        while max_value >= 10:
            max_value /= 10
            digits += 1
        space = self.fontMetrics().width('9') * digits + 50
        return space

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def highlightCurrentLine(self):
        extraSelections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor("#3B4252").lighter(100)
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)

        painter.fillRect(event.rect(), QBrush(QColor(0, 0, 0, 0)))

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        # Just to make sure I use the right font
        height = self.fontMetrics().height()
        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):
                number = str(blockNumber + 1) + "\t\t"
                painter.setPen(QColor("#8FBCBB").lighter(100))
                painter.drawText(0, top, self.lineNumberArea.width(), height, Qt.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1
#-------------------------------------------------------------------------------------------------#

class Tab(QWidget):
    def __init__(self, fileName, filePath, contents):
        super(Tab, self).__init__()
        global usedNums
        self.fileName = ""
        self.fileLocation = ""
        if fileName == "":
            numToUse = -1
            for i in range(1, 1000):
                if usedNums[i] == False:
                    numToUse = i
                    usedNums[i] = True
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
        # variable to store the contents of the text box
        self.contents = contents
        # variable to store the word count of the document
        self.wordCount = 0
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
    
    # event filter to detect right click
    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            # if we right click we want to remove that tab
            if event.button() == QtCore.Qt.RightButton:
                # get the index of the tab we want to close
                tabIndex = -1
                for tab in tabArr:
                    if tab == self:
                        tabIndex = tabArr.index(tab)
                        break
                mainWin.closeTab(tabIndex, currentActiveTextBox)
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
        for i in range(0, len(tabArr)):
            # if we find the right tab we know which textbox to display
            if tabArr[i] == self:
                mainWin.displayTextBox(i)
            # if it's not the right tab then color it in the unfocused color
            else:
                tabArr[i].tabButton.setStyleSheet("""
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
        titleBar.title.setText(self.fileName)

class TextPreview(QPlainTextEdit):
    def __init__(self, parent):
        super(TextPreview, self).__init__()
        self.parent = parent
        self.setMouseTracking(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWordWrapMode(0)
    
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

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.keyPressEvent = self.keyPressEvent
        # store the main window widget
        global mainWin
        global tabCount
        global tabBar
        mainWin = self
        # set the opacity
        self.setWindowOpacity(1.0)
        # vertical layout
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        # add the title bar
        self.layout.addWidget(MyBar(self))
        # create a horizontal layout to represent the tab bar
        self.tabLayout = QHBoxLayout()
        self.tabLayout.addStretch(-1)
        # left, top, right, bottom
        # pad the left and right so we can still resize from that location
        #self.tabLayout.setContentsMargins(MARGIN,0,MARGIN,0)
        # add the tab bar to the vertical layout
        self.layout.addLayout(self.tabLayout)   
        # add drop shadow
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(6)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(2)
        self.shadow.setColor(QColor(0, 0, 0, 200))
        # add a drop shadow before the next thing
        self.dropShadow = QLabel("")
        self.dropShadow.setStyleSheet("""
        background-color: #2E3440;
        border: none;
        
                                        """)
        self.dropShadow.setFixedHeight(1)
        self.dropShadow.setGraphicsEffect(self.shadow)
        self.layout.addWidget(self.dropShadow)
        tabBar = self.tabLayout
        # add the textbox to the vertical layout
        self.textbox = QCodeEditor()
        #self.textbox = Editor()
        #first create the new textbox widget
        self.textbox.setStyleSheet("""
            border: none;
            font: 14pt "Consolas";
            color: #D8DEE9;
            selection-background-color: #4C566A;
                                """)
        self.textbox.resize(mainWin.width() - 100, mainWin.height() - 100)
        self.textbox.move(0,0)
        #self.textbox.setLineWrapMode(self.textbox.WidgetWidth)
        self.textbox.setLineWrapMode(0)
        self.textbox.setCursorWidth(3)
        self.textbox.setTabStopWidth(self.textbox.fontMetrics().width(' ') * TAB_SIZE)
        #------------------------------------------------------------------------#
        font = QFont()
        font.setFamily("Consolas")
        font.setFixedPitch( True )
        font.setPointSize( 14 )
        self.textbox.setFont( font )
        #------------------------------------------------------------------------#
        # code for inserting a preview pane on the main window
        # create horizontal layout so we can have 2 plaintextboxes
        self.textlayout = QHBoxLayout()
        # left, top, right, bottom
        self.textlayout.setContentsMargins(0, 10, 0, 0)
        # add the textbox to the horizontal layout to take 80% of the screen
        self.textlayout.addWidget(self.textbox, 80)
        self.previewbox = TextPreview(self)
        self.previewbox.setStyleSheet("""
            border: none;
            font: 3pt "Consolas";
            color: #D8DEE9;
            selection-color: #2E3440;
            selection-background-color: #D8DEE9;
            padding-left: 20px;
                                """)
        previewFont = QFont()
        previewFont.setFamily("Consolas")
        previewFont.setFixedPitch( True )
        previewFont.setPointSize( 4 )
        self.previewbox.setFont( previewFont )
        #self.previewbox.resize(mainWin.width() / 3, mainWin.height() - 100)
        # you cannot type on it
        self.previewbox.setReadOnly(True)
        # don't be able to select it
        self.previewbox.setTextInteractionFlags(Qt.NoTextInteraction)    
        # it can't get bigger than a certain width
        # make the width of the preview pane constant and about the same width as the min/max/close
        # corner buttons
        self.previewbox.setMaximumWidth(175)
        self.previewbox.setMinimumWidth(175)
        # set the tab size to be really small
        self.previewbox.setTabStopWidth(4)
        # add the preview pane to take 20% of the screen
        self.textlayout.addWidget(self.previewbox, 20)
        # add the horizontal box layout to the main vertical layout
        self.layout.addLayout(self.textlayout)
        # create a drop shadow
        self.shadow2 = QGraphicsDropShadowEffect()
        self.shadow2.setBlurRadius(8)
        self.shadow2.setXOffset(0)
        self.shadow2.setYOffset(8)
        self.shadow2.setColor(QColor(0, 0, 0, 200))
        # add a drop shadow before the next thing
        self.dropShadow2 = QLabel("")
        self.dropShadow2.setStyleSheet("""
        background-color: #2E3440;
        border: none;
                                        """)
        self.dropShadow2.setFixedHeight(1)
        self.dropShadow2.setGraphicsEffect(self.shadow2)
        self.layout.addWidget(self.dropShadow2)
        #------------------------------------------------------------------------#
        # add the infobar at the bottom
        self.infobarlayout = QHBoxLayout()
        # add a stretch so we start the buttons on the right
        self.infobarlayout.addStretch(1)
        # start the display from the right
        #self.infobarlayout.addStretch(1)
        # left, top, right, bottom
        self.infobarlayout.setContentsMargins(0, 12, 10, 0)
        self.infobarlayout.setSpacing(0)
        self.infobarlayout.addWidget(WordCountButton(self))
        self.layout.addLayout(self.infobarlayout)
        #------------------------------------------------------------------------#
        # set the layout
        self.setLayout(self.layout)
        # add the initial default tab that will open on launch
        self.newTabEmpty()
        # make the default size be half the window
        self.setGeometry(startingLocation[0], startingLocation[1], startingLocation[0], startingLocation[1])
        #self.layout.setContentsMargins(MARGIN,0,MARGIN,MARGIN)
        # right has no margin because that is where the other widget will be(preview pane)
        self.layout.setContentsMargins(MARGIN,MARGIN,MARGIN,MARGIN)
        # the min height will be 600 x 600
        self.setMinimumSize(600, 600)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.pressing = False
        self.movingPosition = False
        self.resizingWindow = False
        self.start = QPoint(0, 0)
        self.setStyleSheet("""
            background-color: #2E3440;
                          """)
        # flags for starting location of resizing window
        self.left = False
        self.right = False
        self.bottom = False
        self.top = False
        self.bl = False
        self.br = False
        self.tl = False
        self.tr = False
        self.top = False
        self.setMouseTracking(True)
        self.textbox.setMouseTracking(True)
        app.focusChanged.connect(self.on_focusChanged)

        self.shortcut_newTab = QShortcut(QKeySequence('Ctrl+t'), self)
        self.shortcut_newTab.activated.connect(self.newTabEmpty)
        
        self.shortcut_prevTab = QShortcut(QKeySequence('Ctrl+PgUp'), self)
        self.shortcut_prevTab.activated.connect(self.prevTab)

        self.shortcut_nextTab = QShortcut(QKeySequence('Ctrl+PgDown'), self)
        self.shortcut_nextTab.activated.connect(self.nextTab)

        # not ready to implement new window
        #self.shortcut_newWindow = QShortcut(QKeySequence('Ctrl+n'), self)
        #self.shortcut_newWindow.activated.connect(self.newWindow)

        self.shortcut_closeTab = QShortcut(QKeySequence('Ctrl+w'), self)
        self.shortcut_closeTab.activated.connect(self.closeTabHelper)

        self.shortcut_openFile = QShortcut(QKeySequence('Ctrl+o'), self)
        self.shortcut_openFile.activated.connect(self.openFile)

        self.shortcut_saveFile = QShortcut(QKeySequence('Ctrl+s'), self)
        self.shortcut_saveFile.activated.connect(self.saveFile)

        # shortcut to restore window
        self.shortcut_restoreTab = QShortcut(QKeySequence('Ctrl+Shift+t'), self)
        self.shortcut_restoreTab.activated.connect(self.restoreTab)

        # shortcut to save as
        self.shortcut_saveFileAs = QShortcut(QKeySequence('Ctrl+Shift+s'), self)
        self.shortcut_saveFileAs.activated.connect(self.saveFileAs)

        # shortcut to open tabs with ctrl+number
        self.shortcut_tab1 = QShortcut(QKeySequence('Ctrl+1'), self)
        self.shortcut_tab1.activated.connect(lambda: self.tabJump(1))
        self.shortcut_tab2 = QShortcut(QKeySequence('Ctrl+2'), self)
        self.shortcut_tab2.activated.connect(lambda: self.tabJump(2))
        self.shortcut_tab3 = QShortcut(QKeySequence('Ctrl+3'), self)
        self.shortcut_tab3.activated.connect(lambda: self.tabJump(3))
        self.shortcut_tab4 = QShortcut(QKeySequence('Ctrl+4'), self)
        self.shortcut_tab4.activated.connect(lambda: self.tabJump(4))
        self.shortcut_tab5 = QShortcut(QKeySequence('Ctrl+5'), self)
        self.shortcut_tab5.activated.connect(lambda: self.tabJump(5))
        self.shortcut_tab6 = QShortcut(QKeySequence('Ctrl+6'), self)
        self.shortcut_tab6.activated.connect(lambda: self.tabJump(6))
        self.shortcut_tab7 = QShortcut(QKeySequence('Ctrl+7'), self)
        self.shortcut_tab7.activated.connect(lambda: self.tabJump(7))
        self.shortcut_tab8 = QShortcut(QKeySequence('Ctrl+8'), self)
        self.shortcut_tab8.activated.connect(lambda: self.tabJump(8))
        self.shortcut_tab9 = QShortcut(QKeySequence('Ctrl+9'), self)
        self.shortcut_tab9.activated.connect(lambda: self.tabJump(9))
        self.shortcut_tab10 = QShortcut(QKeySequence('Ctrl+0'), self)
        self.shortcut_tab10.activated.connect(lambda: self.tabJump(10))

        # shortcut to snap the window to left, right, up, down, and corners
        self.shortcut_snapLeft = QShortcut(QKeySequence('Ctrl+Alt+Left'), self)
        self.shortcut_snapLeft.activated.connect(lambda: self.snapWin("left"))
        self.shortcut_snapRight = QShortcut(QKeySequence('Ctrl+Alt+Right'), self)
        self.shortcut_snapRight.activated.connect(lambda: self.snapWin("right"))
        self.shortcut_snapTop = QShortcut(QKeySequence('Ctrl+Alt+Up'), self)
        self.shortcut_snapTop.activated.connect(lambda: self.snapWin("top"))
        self.shortcut_snapBottom = QShortcut(QKeySequence('Ctrl+Alt+Down'), self)
        self.shortcut_snapBottom.activated.connect(lambda: self.snapWin("bottom"))

        # detect if there was a change in the active text edit, and if so change the corresponding
        # tab's isSaved to False
        self.textbox.textChanged.connect(self.setSavedToFalse)
        # to help rounded corners work
        self.setAttribute(Qt.WA_TranslucentBackground)
    
    def snapWin(self, direction):
        global rightDown
        global leftDown
        global upDown
        global downDown
        global isMaximized
        # start with this so that we can maximize and restore over and over with the up button
        self.showNormal()
        isMaximized = False
        # get the current working resolution to account for things like the taskbar
        monitor_info = GetMonitorInfo(MonitorFromPoint((0,0)))
        working_resolution = monitor_info.get("Work")
        workingWidth = working_resolution[2]
        workingHeight = working_resolution[3]
        
        # middle window from right
        if direction == "left" and rightDown == True:
            self.setGeometry(workingWidth/4, 0, workingWidth/2, workingHeight)
            # set the m all to false
            rightDown = False
            leftDown = False
            downDown = False
            upDown = False
        
        # middle window from left
        elif direction == "right" and leftDown == True:
            self.setGeometry(workingWidth/4, 0, workingWidth/2, workingHeight)
            # set the m all to false
            rightDown = False
            leftDown = False
            downDown = False
            upDown = False
        
        # snap the window left
        elif direction == "right" and downDown == False and upDown == False:
            self.setGeometry(workingWidth/2, 0, workingWidth/2, workingHeight)
            # set the right to true and the others to false
            rightDown = True
            leftDown = False
            downDown = False
            upDown = False
        
        # snap bottom right from bottom
        elif direction == "right" and downDown == True and upDown == False:
            self.setGeometry(workingWidth/2, workingHeight/2, workingWidth/2, workingHeight/2)
            # set all to false
            rightDown = False
            leftDown = False
            downDown = False
            upDown = False
        
        # snap bottom right from right
        elif direction == "bottom" and leftDown == False and rightDown == True:
            self.setGeometry(workingWidth/2, workingHeight/2, workingWidth/2, workingHeight/2)
            # set all to false
            rightDown = False
            leftDown = False
            downDown = False
            upDown = False

        # snap bottom left from bottom
        elif direction == "left" and downDown == True and upDown == False:
            self.setGeometry(0, workingHeight/2, workingWidth/2, workingHeight/2)
            # set all to false
            rightDown = False
            leftDown = False
            downDown = False
            upDown = False
        
        # snap bottom left from left
        elif direction == "bottom" and leftDown == True and rightDown == False:
            self.setGeometry(0, workingHeight/2, workingWidth/2, workingHeight/2)
            # set all to false
            rightDown = False
            leftDown = False
            downDown = False
            upDown = False
        
        # snap top left from top
        elif direction == "left" and downDown == False and upDown == True:
            self.setGeometry(0, 0, workingWidth/2, workingHeight/2)
            # set all to false
            rightDown = False
            leftDown = False
            downDown = False
            upDown = False
        
        # snap top left from left
        elif direction == "top" and leftDown == True and rightDown == False:
            self.setGeometry(0, 0, workingWidth/2, workingHeight/2)
            # set all to false
            rightDown = False
            leftDown = False
            downDown = False
            upDown = False
        
        # snap top right from top
        elif direction == "right" and downDown == False and upDown == True:
            self.setGeometry(workingWidth/2, 0, workingWidth/2, workingHeight/2)
            # set all to false
            rightDown = False
            leftDown = False
            downDown = False
            upDown = False
        
        # snap top right from right
        elif direction == "top" and leftDown == False and rightDown == True:
            self.setGeometry(workingWidth/2, 0, workingWidth/2, workingHeight/2)
            # set all to false
            rightDown = False
            leftDown = False
            downDown = False
            upDown = False

        # snap left
        elif direction == "left" and downDown == False and upDown == False:
            self.setGeometry(0, 0, workingWidth/2, workingHeight)
            # set left to true and others to false
            leftDown = True
            rightDown = False
            downDown = False
            upDown = False
        
        # maximize
        elif direction == "top" and upDown == True:
            # click the max button
            self.setGeometry(0, 0, workingWidth, workingHeight)
            isMaximized = True
            #self.layout.itemAt(0).widget().btn_max_clicked()
            # set all to false
            rightDown = False
            leftDown = False
            downDown = False
            upDown = False

        # snap up
        elif direction == "top" and leftDown == False and rightDown == False:
            self.setGeometry(0, 0, workingWidth, workingHeight / 2)
            # set up to True and all others to false
            upDown = True
            leftDown = False
            rightDown = False
            downDown = False
        
        # minimize
        elif direction == "bottom" and downDown == True:
            # click the min button
            self.layout.itemAt(0).widget().btn_min_clicked()
            # set all to false
            rightDown = False
            leftDown = False
            downDown = False
            upDown = False

        # snap down
        elif direction == "bottom" and leftDown == False and rightDown == False:
            self.setGeometry(0, workingHeight / 2, workingWidth, workingHeight / 2)
            # set Down to True and all others to false
            downDown = True
            upDown = False
            leftDown = False
            rightDown = False
            

    def paintEvent(self, ev):
        painter = QPainter(self)
        painter.setBrush(QColor("#2E3440"))
        # removes the black border around the window
        painter.setPen(QColor(0,0,0,0))
        rect = QRectF(ev.rect())
        painter.drawRoundedRect(rect, 10, 10)   

    def tabJump(self, index):
        if len(tabArr) > index-1:
            tabArr[index-1].tabClicked()

    def saveFileAs(self):
        global tabArr
        global isShortCut
        isShortCut = True
        tabArr[currentActiveTextBox].isSaved = False
        tabArr[currentActiveTextBox].filePath = ""
        self.saveFile()

    def restoreTab(self):
        global tabStack
        global isShortCut 
        isShortCut = True
        if len(tabStack) > 0:            
            oldTab = tabStack.pop()
            self.newTab(oldTab.fileName, oldTab.filePath, oldTab.contents)

    def setSavedToFalse(self):
        global isShortCut
        global tabArr
        # if the last thing pressed was a shortcut we don't really have to do anything since there
        # are no text differences to store
        if isShortCut:
            isShortCut = False
        # if it was not a shortcut then we store the text differences
        else:            
            tabArr[currentActiveTextBox].isSaved = False
            # update the values in the textbox array
            tabArr[currentActiveTextBox].contents = self.textbox.toPlainText()
        # update the values in the preview box
        self.previewbox.setPlainText(self.textbox.toPlainText())
        # update the value of the word count
        mainWin.infobarlayout.itemAt(wordCountIndex).widget().setText(str(tabArr[currentActiveTextBox].wordCount))

    def saveFile(self):
        global currentActiveTextBox
        global isShortCut
        isShortCut = True
        
        # only save if there have been changes
        if tabArr[currentActiveTextBox].isSaved == False:
            tabFound = False
            # if the file I am working on is new then open dialog
            if tabArr[currentActiveTextBox].filePath == "":
                aTuple = QFileDialog.getSaveFileName(self, 'Save As: ', '', 'All Files (*)')
                filePath = aTuple[0]
                # check if the file being saved is already open in the editor
                # if it is then just save that tab and mark it as found
                for tab in tabArr:
                    if tab.filePath == filePath:
                        tabFound = True
                        curTab = tabArr.index(tab)

                # store the filePath
                tabArr[currentActiveTextBox].filePath = filePath
            # if the file is not new then the dialog won't pop up because this isn't save as
            else:
                filePath = tabArr[currentActiveTextBox].filePath
            if filePath != '':
                # get the name of the file
                name = filePath
                end = len(name) - 1
                c = name[end]
                start = end
                while c != '/' and c != '"\"':
                    start -= 1
                    c = name[start]
                finalName = ''
                for i in range(start+1, end +1 ):
                    finalName = finalName + name[i]

                # this only applies to the default name tabs, since otherwise when you save the name
                # stays the same
                if tabArr[currentActiveTextBox].fileName != finalName:
                    tabArr[currentActiveTextBox].fileName = finalName

                tabArr[currentActiveTextBox].tabButton.setText(finalName)

                f = open(filePath, "w")
                if tabFound:
                    # change the contents of the original file
                    f.write(tabArr[curTab].contents)
                    # set the isSaved indicator to True
                    tabArr[curTab].isSaved = True
                    # store the tab we want to land on
                    tempTab = tabArr[curTab]
                    tabArr[currentActiveTextBox].isSaved = True
                    # finally close the current active tab 
                    self.closeTab()
                    # now move to the tab we were on
                    tempTab.tabClicked()
                else:
                    f.write(tabArr[currentActiveTextBox].contents)
                    tabArr[currentActiveTextBox].isSaved = True
                    # click on it so that the title of the window changes to match the tab
                    tabArr[currentActiveTextBox].tabClicked()

                f.close()

    def openFile(self):
        global isShortCut
        isShortCut = True
        #QFileDialog.getOpenFileName(self, "Files", "All Files (*)")
        aTuple = QFileDialog.getOpenFileName(self, 'Open: ', '', 'All Files (*)')
        if aTuple[0] != '':
            # read the contents of the file into a variable
            with open(aTuple[0]) as f:
            #   lines = f.readlines()
                content = f.read()
            f.close()

            tabFound = False
            # see if you are opening a file that is already open in the editor
            for tab in tabArr:
                if tab.filePath == aTuple[0]:
                    tabFound = True
                    tab.tabClicked()
            if tabFound == False:
                # get the name of the file
                name = aTuple[0]
                end = len(name) - 1
                c = name[end]
                start = end
                while c != '/' and c != '"\"':
                    start -= 1
                    c = name[start]
                finalName = ''
                for i in range(start+1, end +1 ):
                    finalName = finalName + name[i]
                # create a new tab with the name of the file that was opened
                self.newTab(finalName, aTuple[0], content)
                # put the cursor at the end of the text
                self.textbox.moveCursor(QTextCursor.End)

    def closeTabHelper(self):
        self.closeTab(currentActiveTextBox, currentActiveTextBox)

    def closeTab(self, tabToClose, currentActiveTab):
        global currentActiveTextBox
        global tabCount
        global curEmptyTab
        global numToUse
        global tabArr
        global tabBar
        global isShortCut
        isShortCut = True
    
        # for storing closed tabs to be able to restore them
        global tabStack
        okayToClose = True
        isCancelled = False
        
        # if we are closing a tab that is not active we just need to set it to active
        # and store the index of the tab we want to go back to
        returnIndex = -1
        if currentActiveTab != tabToClose:
            # if the current active tab is greater then its index will decrease by 1 when we remove
            # the other tab
            if currentActiveTab > tabToClose:
                returnIndex = currentActiveTab - 1
            else:
                returnIndex = currentActiveTab
            # change the CATB to be the tab we want to close
            currentActiveTextBox = tabToClose

        # if it is just an untitled empty page, we can set it as saved since nothing is lost
        if "untitled" in tabArr[currentActiveTextBox].fileName and tabArr[currentActiveTextBox].contents == "":
            tabArr[currentActiveTextBox].isSaved = True
    
        # check that tab isSaved before deleting it
        if tabArr[currentActiveTextBox].isSaved == False:
            msg = QMessageBox()
            msg.setWindowTitle("Notes")
            msg.setText("Do you want to save changes before closing?")
            msg.setStandardButtons(QMessageBox.Save | QMessageBox.No | QMessageBox.Cancel)
            msg.setDefaultButton(QMessageBox.Save)
            msg.setIcon(QMessageBox.Question)
            # cancel = 4194304
            # no = 65536
            # else yes lol
            QApplication.setOverrideCursor(Qt.ArrowCursor)
            ans = msg.exec_()
            # they would not like to save before closing
            if ans == 65536:
                okayToClose = True
            # they would like to cancel
            elif ans == 4194304:
                isCancelled = True
            # if they would like to save
            else:
                okayToClose = False
            QApplication.setOverrideCursor(Qt.IBeamCursor)
            
        if isCancelled == False:    
            # close tab and textbox at currentactivetextbox
            if len(tabArr) > 1 and okayToClose:
                # remove the tab from the tab bar
                self.tabLayout.removeWidget(tabArr[currentActiveTextBox])
                # remove the tab from the tab array
                if "untitled" in tabArr[currentActiveTextBox].fileName:
                    # get the number of the untitled tab
                    temp = tabArr[currentActiveTextBox].fileName
                    index = temp.index('_')
                    c = temp[index + 1]
                    curEmptyTab = ""
                    counter = 0
                    while c != '.':
                        counter += 1
                        curEmptyTab += c
                        c = temp[index + 1 + counter]
                    # mark this number of unused tab as unused
                    usedNums[int(curEmptyTab)] = False 
                # find the correct tab to remove
                for tabs in tabArr:
                    if tabs == tabArr[currentActiveTextBox]:
                        #tabStack.append(copy.deepcopy(tabs))
                        tabs.deleteLater()
                # store the tab and textbox contents
                tabStack.append(tabArr[currentActiveTextBox])
                # remove the tab from the tabarray
                tabArr.remove(tabArr[currentActiveTextBox])
                tabCount -= 1
                # if we removed the last tab close the program
                if len(tabArr) == 0:
                    self.close()
                # if we removed a non active tab then just restore the appropriate tab
                if returnIndex != -1:
                    currentActiveTextBox = returnIndex + 1
                # if the tab we just removed is the first tab
                if currentActiveTextBox == 0:
                    # just shift over to the tab to its right by staying at index 0
                    tabArr[currentActiveTextBox].tabClicked()

                # if we just removed the last tab
                elif currentActiveTextBox == len(tabArr):
                    # we just shift over to the left
                    tabArr[currentActiveTextBox - 1].tabClicked()
                
                # finally if we remove any old random tab around the middle
                else:
                    # use the tab on the left
                    tabArr[currentActiveTextBox - 1].tabClicked()
            
            # if we press close when there is one tab or 0 tabs we just close the window if it's okay
            elif len(tabArr) == 1 and okayToClose:
                self.close()
            
            # otherwise they want to save, so we can call on the save function
            else:
                self.saveFile()

    def nextTab(self):
        global isShortCut
        isShortCut = True
        if tabCycle == True:
            # if we are on the last text box we cant go out of bounds
            if currentActiveTextBox < len(tabArr) - 1: 
                if len(tabArr) > 1:
                    tabArr[currentActiveTextBox + 1].tabClicked()
            # if we are on the very last text box
            else:
                # and there is more than 1 box
                if len(tabArr) > 1:
                    tabArr[0].tabClicked()
        # if we don't want to cycle we just do the same as above except we do nothing if we are at 0
        else:
             # if we are on the first text box we cant go into the negatives so we display the last one
            if currentActiveTextBox < len(tabArr) - 1: 
                if len(tabArr) > 1:
                    tabArr[currentActiveTextBox + 1].tabClicked()

    def prevTab(self):
        global isShortCut
        isShortCut = True
        if tabCycle == True:
            # if we are on the first text box we cant go into the negatives so we display the last one
            if currentActiveTextBox > 0: 
                if len(tabArr) > 1:
                    tabArr[currentActiveTextBox - 1].tabClicked()
            # if we are on the very first text box
            else:
                # and there is more than 1 box
                if len(tabArr) > 1:
                    tabArr[len(tabArr) - 1].tabClicked()
        # if we don't want to cycle we just do the same as above except we do nothing if we are at 0
        else:
             # if we are on the first text box we cant go into the negatives so we display the last one
            if currentActiveTextBox > 0: 
                if len(tabArr) > 1:
                    tabArr[currentActiveTextBox - 1].tabClicked()

    def displayTextBox(self, index):
        global currentActiveTextBox
        
        global tabArr
        # make the tab that was clicked the active one
        currentActiveTextBox = index
        # restore the text that there was on that tab
        self.textbox.setPlainText(tabArr[currentActiveTextBox].contents)
        # restore the correct word count
        self.infobarlayout.itemAt(wordCountIndex).widget().setText(str(tabArr[currentActiveTextBox].wordCount))
        # put the cursor at the end of the text
        self.textbox.moveCursor(QTextCursor.End)
        # make the textbox the focus
        #self.layout.itemAt(textBoxIndex).widget().setFocus()
        self.layout.itemAt(textBoxIndex).itemAt(0).widget().setFocus()

    # add a new textbox to go along with this tab making this tab the parent of that textbox
    def addTextBox(self, contents):  
        
        global currentActiveTextBox
        # update the current active text box
        currentActiveTextBox = len(tabArr) - 1
        # add the contents to the textbox
        self.textbox.setPlainText(contents)
        # add the contents to the preview pane
        self.previewbox.setPlainText(contents)
        # add the correct wordcount for the tab (will be 0 if new tab)
        self.infobarlayout.itemAt(wordCountIndex).widget().setText(str(tabArr[currentActiveTextBox].wordCount))
        # focus the cursor on the new text box
        self.textbox.setFocus()

    def newTab(self, name, filePath, contents):
        global tabCount
        global tabArr
        
        global isShortCut
        isShortCut = True
        tab = Tab(name, filePath, contents)
        tabArr.append(tab)        
        mainWin.tabLayout.insertWidget(tabCount, tab)
        tabCount += 1
        self.addTextBox(contents)

    def newTabEmpty(self):
        global tabCount
        global tabArr
        
        global isShortCut
        isShortCut = True
        tab = Tab("", "", "")
        tabArr.append(tab)
        mainWin.tabLayout.insertWidget(tabCount, tab)
        tabCount += 1
        self.addTextBox("")

    def on_focusChanged(self, old, new):
        # set the opacity to 1 if not focused
        if self.isActiveWindow():
            self.setWindowOpacity(0.98)
        else:
            self.setWindowOpacity(1.0)

    def mousePressEvent(self, event):
        pos = event.pos()
        # set pressing to true
        self.pressing = True
        if isMaximized == False:
            # if they clicked on the edge then we need to change pressing to true and resizingWindow to
            # true and we need to change the cursor shape
            # top left
            if pos.x() <= 8 and pos.y() <= 8:
                self.resizingWindow = True
                self.start = event.pos()
                self.tl = True
            # top right
            elif pos.x() >= self.width() - 8 and pos.y() <= 8:
                self.resizingWindow = True
                self.start = event.pos()
                self.tr = True
            # top
            elif pos.y() <= 8 and pos.x() > 8 and pos.x() < self.width() - 8:
                self.resizingWindow = True
                self.start = event.pos().y()
                self.top = True     
            elif pos.y() >= self.height() - 8 and pos.x() <= 8 and pos.y() > 8:
                self.resizingWindow = True
                self.start = event.pos()
                self.bl = True
            elif pos.x() <= 8 and pos.y() > 8:
                self.resizingWindow = True
                self.start = event.pos().x()
                self.left = True   
            elif pos.x() >= self.width() - 8 and pos.y() >= self.height() - 8:
                self.resizingWindow = True
                self.start = event.pos()
                self.br = True    
            elif pos.x() >= self.width() - 8 and pos.y() > 8:
                self.resizingWindow = True
                self.start = event.pos().x()
                self.right = True              
            elif pos.x() > 8 and pos.x() < self.width() - 8 and pos.y() >= self.height() - 8:
                self.resizingWindow = True
                self.start = event.pos().y()
                self.bottom = True       
  
    def mouseMoveEvent(self, event):
        pos = event.pos()
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        if isMaximized == False:
            # top left
            if pos.x() <= 10 and pos.y() <= 10:
                QApplication.setOverrideCursor(Qt.SizeFDiagCursor)
            # top right
            elif pos.x() >= self.width() - 8 and pos.y() <= 8:
                QApplication.setOverrideCursor(Qt.SizeBDiagCursor)
            # top
            elif pos.y() <= 5 and pos.x() > 5 and pos.x() < self.width() - 5:
                QApplication.setOverrideCursor(Qt.SizeVerCursor)
            # bottom left
            elif pos.y() >= self.height() - 8 and pos.x() <= 8:
                QApplication.setOverrideCursor(Qt.SizeBDiagCursor)
            # bottom right
            elif pos.x() >= self.width() - 8 and pos.y() >= self.height() - 8:
                QApplication.setOverrideCursor(Qt.SizeFDiagCursor)
            # bottom
            elif pos.x() > 0 and pos.x() < self.width() - 8 and pos.y() >= self.height() - 8:
                QApplication.setOverrideCursor(Qt.SizeVerCursor)
            # left
            elif pos.x() <= 5 and pos.y() > 5:
                QApplication.setOverrideCursor(Qt.SizeHorCursor)
            # right
            elif pos.x() >= self.width() - 5 and pos.y() > 5:
                QApplication.setOverrideCursor(Qt.SizeHorCursor)
            else:
                QApplication.setOverrideCursor(Qt.ArrowCursor)
        # if they are resizing
        # need to subtract the movement from the width/height 
        # but I also need to account for if they are resizing horizontally from the left or
        # vertically from the top because I need to shift the window to the right/down the same amount
        if self.pressing and self.resizingWindow:
            # resize from the top
            if self.top == True:
                # resize from the top
                if self.height() - event.pos().y() >= 600:
                    self.setGeometry(self.pos().x(), self.pos().y() + event.pos().y(), self.width(), self.height() - event.pos().y())
            # resize from the top left
            if self.tl == True:
                # move both dimensions if both boundaries are okay
                if self.width() - event.pos().x() >= 600 and self.height() - event.pos().y() >= 600:
                    self.setGeometry(self.pos().x() + event.pos().x(), self.pos().y() + event.pos().y(), self.width() - event.pos().x(), self.height() - event.pos().y())
                # move only top if width is already at its smallest
                elif self.height() - event.pos().y() >= 600:
                    self.setGeometry(self.pos().x(), self.pos().y() + event.pos().y(), self.width(), self.height() - event.pos().y())
                # move only left if height is at its smallest
                elif self.width() - event.pos().x() > 600:
                    self.setGeometry(self.pos().x() + event.pos().x(), self.pos().y(), self.width() - event.pos().x(), self.height())
            
            # resize top right
            if self.tr == True:
                pos = event.pos().x() 
                # top right
                if self.height() - event.pos().y() >= 600 and self.width() >= 600:
                    self.setGeometry(self.pos().x(), self.pos().y() + event.pos().y(), pos, self.height() - event.pos().y())

                # resize from the top
                elif self.height() - event.pos().y() >= 600:
                    self.setGeometry(self.pos().x(), self.pos().y() + event.pos().y(), self.width(), self.height() - event.pos().y())
                elif self.width() >= 600:
                    self.setGeometry(self.pos().x(), self.pos().y(), pos, self.height()) 

            # resize from the left to the right
            if self.left == True:
                # resize from the left
                if self.width() - event.pos().x() > 600:
                    self.setGeometry(self.pos().x() + event.pos().x(), self.pos().y(), self.width() - event.pos().x(), self.height())
            # resize from the right
            if self.right == True:
                pos = event.pos().x()
                if self.width() >= 600:
                    self.setGeometry(self.pos().x(), self.pos().y(), pos, self.height()) 
            # resize from the bottom
            if self.bottom == True:
                pos = event.pos().y()
                if self.height() >= 600:
                    self.setGeometry(self.pos().x(), self.pos().y(), self.width(), pos) 
            # resize from the bottom right
            if self.br == True:
                pos = event.pos()
                if self.height() >= 600 and self.width() >= 600:
                    self.setGeometry(self.pos().x(), self.pos().y(), pos.x(), pos.y()) 
            # resize from the bottom left
            if self.bl == True:
                pos = event.pos().y()
                if self.width() - event.pos().x() > 600 and self.height() >= 600:
                    self.setGeometry(self.pos().x() + event.pos().x(), self.pos().y(), self.width() - event.pos().x(), pos)
                elif self.height() >= 600:
                    self.setGeometry(self.pos().x(), self.pos().y(), self.width(), pos) 
                elif self.width() - event.pos().x() > 600:
                    self.setGeometry(self.pos().x() + event.pos().x(), self.pos().y(), self.width() - event.pos().x(), self.height())
            
    # if the mouse button is released then tag pressing as false
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            return
        self.pressing = False
        self.movingPosition = False
        self.resizingWindow = False
        self.left = False
        self.right = False
        self.bottom = False
        self.bl = False
        self.br = False
        self.tr = False
        self.tl = False
        self.top = False

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
        if len(tabArr) > 1:
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
        elif len(tabArr) == 1 and tabArr[0].isSaved == False:
            self.parent.closeTab(0, 0)
        # otherwise just close
        else:
            self.parent.close()

    def btn_max_clicked(self):
        global isMaximized

        # if it is clicked while we are currently maximized, then it means we need to revert to
        # lastPosition
        if isMaximized:
            self.parent.showNormal()
            isMaximized = False
        # if it is not maximized
        else:
            # if the maximize button is pressed on the menubar, it should call the maximize function of
            # the parent window. It is a standard function, so it is not written in this code
            self.parent.showMaximized()
            # toggle isMax so we know the state
            isMaximized = True
        # focus on the textbox
        #self.parent.layout.itemAt(textBoxIndex).widget().setFocus()
        self.parent.layout.itemAt(textBoxIndex).itemAt(0).widget().setFocus()

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
        if isMaximized == False:
            self.movingPosition = True
            self.start = self.mapToGlobal(event.pos())

    def mouseMoveEvent(self, event):
        pos = event.pos()
        # top left
        if pos.x() <= 3 and pos.y() <= 3:
            QApplication.setOverrideCursor(Qt.SizeFDiagCursor)
        
        else:
            QApplication.setOverrideCursor(Qt.ArrowCursor)
        if isMaximized == False:
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

# this sets the icon as your taskbar icon
myappid = 'Codap'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

# make the resolution global variables
screen_resolution = 0
width = 0
height = 0
key = ''
res = {}
res["1920x1080"] = [640, 360] # full hd
res["2560x1440"] = [853, 480] # wqhd
res["3440x1440"] = [1147, 480] # ultrawide
res["3840x2160"] = [1160, 720] # 4k
focused = False # variable to track if the gui is focused so it knows to track typing or not
stack = []
# variables to track if modifiers are currently held down
isControlDown = False
isShiftDown = False
isAltDown = False
# variable to track the margins used on the main layout
MARGIN = 5
# variable to make the starting indent on the textbox 
START_INDENT = 50
# tab size
TAB_SIZE = 8
# variable to allow going back to previous size after maximizing
isMaximized = False
# variable to track the tab bar index
tabRowIndex = 1
# variable to track the main textbox index in case I update the layout order
textBoxIndex = 3
# word count index
infoBarIndex = 4
# word count index
wordCountIndex = 1
# variable to track the tabBar so I can access it quickly
# variable to track the number of default tabs currently open
curEmptyTab = 1
# list to store which numbers have been used for default tabs
usedNums = []
for i in range(0, 1000):
    usedNums.append(False)
# variable to track the index of the tab so we know the textbox associated with it
tabCount = 0
# arraf storing the tabs
tabArr = []
# variables to store the mainwindow and title bar
mainWin = 0
titleBar = 0
# index of current active textbox
currentActiveTextBox = 0
# if tabs cycling should wrap around
tabCycle = True
# stack to store closed tabs so we can reopen them
tabStack = []
# variable to store whether the last action was a shortcut so we don't have to save after every
# shortcut
isShortCut = False
# variable to set the cursor flash time
cursorFlashTime = 800
# variable to be able to snap to sides and corners
leftDown = False
upDown = False
downDown = False
rightDown = False

stylesheet2 = """
    QWidget {
        background-image: url("background.png"); 
        background-repeat: no-repeat; 
        background-position: center;
    }
"""
stylesheet = """
    QWidget {
        border-radius:50px;
    }
"""

if __name__ == "__main__":
    app = QApplication(sys.argv)
    #app.setStyleSheet(stylesheet2)
    app.setCursorFlashTime(cursorFlashTime)
    
    screen_resolution = app.desktop().screenGeometry()
    print(screen_resolution)
    width, height = screen_resolution.width(), screen_resolution.height()
    key = str(width) + "x" + str(height)
    startingLocation = []
    if key not in res:
        startingLocation = [500, 500]
    else:
        startingLocation = res[key]
    mw = MainWindow()
    mw.show()
    # make the textbox be automatically in focus on startup
    #mainWin.layout.itemAt(textBoxIndex).widget().setFocus()
    mainWin.layout.itemAt(textBoxIndex).itemAt(0).widget().setFocus()

    sys.exit(app.exec_())