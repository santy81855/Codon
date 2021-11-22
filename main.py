import sys
# to get the working monitor size
from win32api import GetMonitorInfo, MonitorFromPoint
import TitleBar, Tab, WordCount, PreviewPane, TextBox
from PyQt5.Qsci import QsciScintilla, QsciLexerPython

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
        self.layout.addWidget(TitleBar.MyBar(self))
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
        self.textbox = TextBox.Editor()
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
        self.textlayout.setContentsMargins(30, 10, 0, 0)
        # add the textbox to the horizontal layout to take 80% of the screen
        self.textlayout.addWidget(self.textbox, 80)
        self.previewbox = PreviewPane.TextPreview(self)
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
            # update the cursor position
            tabArr[currentActiveTextBox].cursorPosition = self.textbox.textCursor().position()
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
        # put the cursor where we left it 
        self.textbox.moveCursor(QTextCursor.End)
        # make the textbox the focus
        #self.layout.itemAt(textBoxIndex).widget().setFocus()
        self.layout.itemAt(textBoxIndex).itemAt(0).widget().setFocus()

    # idek
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
# list of special characters
special_characters = "!@#$%^&*()-+?_=.:;,<>/\"'}{~`[]"
# list of python keywords
numbersList = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
python_keywords = ['False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await', 'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield']
c_keywords = ['auto', 'double', 'int', 'struct', 'break', 'else', 'long', 'switch', 'case', 'enum', 'register', 'typedef', 'const', 'extern', 'return', 'union', 'char', 'float', 'short', 'unsinged', 'continue', 'for', 'signed', 'volatile', 'default', 'goto', 'sizeof', 'void', 'do', 'if', 'static', 'while', '!', '@', '#', '$', '%', '^', '&', '*', '-', '+', '?', '_', '=', '.', ':', ';', ',', '<', '>', '/', '\"', '~', '`']
java_keywords = [
'abstract', 'continue', 'for', 'new', 'switch', 'assert', 'default', 'goto', 'package', 'synchronized', 'boolean', 'do', 'if', 'private', 'this', 'break', 'double', 'implements', 'protected', 'throw', 'byte', 'else', 'import', 'public', 'throws', 'case', 'enum', 'instanceof', 'return', 'transient', 'catch', 'extends', 'int', 'short', 'try', 'char', 'final', 'interface', 'static', 'void', 'class', 'finally', 'long', 'strictfp', 'volatile', 'const', 'float', 'native', 'super', 'while', '!', '@', '#', '$', '%', '^', '&', '*', '-', '+', '?', '_', '=', '.', ':', ';', ',', '<', '>', '/', '\"', "'", '~', '`'] 
js_keywords = ['abstract', 'arguments', 'await', 'boolean', 'break', 'byte', 'case', 'catch', 'char', 'class', 'const', 'continue', 'debugger', 'default', 'delete', 'do', 'double', 'else', 'enum', 'eval', 'export', 'extends', 'false', 'final', 'finally', 'float', 'for', 'function', 'goto', 'if', 'implements', 'import', 'in', 'instanceof', 'int', 'interface', 'let', 'long', 'native', 'new', 'null', 'package', 'private', 'protected', 'public', 'return', 'short', 'static', 'super', 'switch', 'synchronized', 'this', 'throw', 'throws', 'transient', 'true', 'try', 'typeof', 'var', 'void', 'volatile', 'while', 'with', 'yield', '!', '@', '#', '$', '%', '^', '&', '*', '-', '+', '?', '_', '=', '.', ':', ';', ',', '<', '>', '/', '\"', '~', '`']
cs_keywords = ['abstract','as','base','bool','break','byte','case','catch','char','checked','class','const','continue','decimal','default','delegate','do','double','else','enum','','event','explicit','extern','false','finally','fixed','float','for','foreach','goto','if','implicit','in','int','interface','internal','is','lock','long','','namespace','new','null','object','operator','out','override','params','private','protected','public','readonly','ref','return','sbyte','sealed','short','sizeof','stackalloc','','static','string','struct','switch','this','throw','true','try','typeof','uint','ulong','unchecked','unsafe','ushort','using','virtual','void','volatile','while', '!', '@', '#', '$', '%', '^', '&', '*', '-', '+', '?', '_', '=', '.', ':', ';', ',', '<', '>', '/', '\"', '~', '`']

# variables for color settings
bracketColor = "#D08770"
keywordColor = "#A3BE8C"
parenColor = "#EBCB8B"
braceColor = "#D08770"
functionColor = "#88C0D0"
commentColor = "#B48EAD"
textColor = "#D8DEE9"
stringColor = "#8FBCBB"
numberColor = "#BF616A"

# create a dictionary with the colors used for different languages syntax highlighting
keywords = {}
keywords["py"] = python_keywords
keywords["c"] = c_keywords
keywords["cpp"] = c_keywords
keywords["java"] = java_keywords
keywords["js"] = js_keywords
keywords["cs"] = cs_keywords

# global variables to track comments
singleLineComment = False
multiLineComment = False
# global variable to track strings
isString = False

# create dictionary for the character to represent comments for each language
commentChar = {}
commentChar["py"] = ["#", "'''", "'''"]
commentChar["c"] = ["//", "/*", "*/"]
commentChar["cpp"] = ["//", "/*", "*/"]
commentChar["cs"] = ["//", "/*", "*/"]
commentChar["java"] = ["//", "/*", "*/"]
commentChar["js"] = ["//", "/*", "*/"]


stylesheet2 = """
    QWidget {
        background-image: url("background.png"); 
        background-repeat: no-repeat; 
        background-position: center;
    }
"""

if __name__ == "__main__":
    app = QApplication(sys.argv)
    #app.setStyleSheet(stylesheet2)
    app.setCursorFlashTime(cursorFlashTime)
    
    screen_resolution = app.desktop().screenGeometry()
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