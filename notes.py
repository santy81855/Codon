import sys
from PyQt5 import QtCore
from PyQt5 import QtGui
#

#
from PyQt5.QtGui import QCursor, QMouseEvent, QFont, QKeySequence
from PyQt5.QtCore import QPoint, pyqtSignal
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QObject, QMimeData
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QCompleter, QFileDialog
from PyQt5.QtWidgets import QHBoxLayout, QTextEdit, QPlainTextEdit, QShortcut
from PyQt5.QtWidgets import QLabel, QStackedWidget, QMessageBox
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget
import textwrap
from pynput import keyboard
import string

#-------------------------------------------------------------------------------------------------#

#-------------------------------------------------------------------------------------------------#

class Tab(QWidget):
    def __init__(self, fileName, filePath):
        super(Tab, self).__init__()
        global numEmptyTabs
        self.fileName = ""
        self.fileLocation = ""
        if fileName == "":
            self.fileName = "untitled_" + str(numEmptyTabs + 1) + ".txt"
            numEmptyTabs += 1
        else:
            self.fileName = fileName
        # add the file path
        if filePath == "":
            self.filePath = ""
        else:
            self.filePath = filePath
        self.isSaved = False
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
            background-color: #4C566A;
            color: #D8DEE9;
            font: 14pt "Consolas";
            border: none;
            padding: 10px;
            }
            QPushButton::hover
            {
            background-color: #ECEFF4;
            color: #2E3440;
            border: none;
            padding: 10px;
            }-  
                                    """)
        self.setMouseTracking(True)
        self.singleTabLayout.addWidget(self.tabButton)
        self.setLayout(self.singleTabLayout)
        # left, top, right, bottom
        self.singleTabLayout.setContentsMargins(0,0,0,0)        
        self.tabClicked()

    def tabClicked(self):
        # when we click the tab, we want to focus the tab by changing its color to be the same as
        # the background
        self.tabButton.setStyleSheet("""
            QPushButton
            {
            background-color: #D8DEE1;
            color: #4C566A;
            font: 14pt "Consolas";
            border: none;
            padding: 10px;
            }
            QPushButton::hover
            {
            background-color: #ECEFE1;
            color: #2E3440;
            border: none;
            padding: 10px;
            }-  
                                    """)
        # Go to the contents of the tab that was clicked
        for i in range(0, len(tabArr)):
            # if we find the right tab we know which textbox to display
            if tabArr[i] == self:
                print("here on tab {}".format(i))
                mainWin.displayTextBox(i)
            # if it's not the right tab then color it in the unfocused color
            else:
                tabArr[i].tabButton.setStyleSheet("""
            QPushButton
            {
            background-color: #4C566A;
            color: #D8DEE9;
            font: 14pt "Consolas";
            border: none;
            padding: 10px;
            }
            QPushButton::hover
            {
            background-color: #ECEFF4;
            color: #2E3440;
            border: none;
            padding: 10px;
            }-  
                                    """)
        
        # change the title of the window to be the tab name
        titleBar.title.setText(self.fileName)
        
# need to change code to have a stackedwidget instead of just a textbox in the TextField
class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        # store the main window widget
        global mainWin
        global tabCount
        mainWin = self
        # set the opacity
        self.setWindowOpacity(0.9)
        # vertical layout
        self.layout = QVBoxLayout()
        # add the title bar
        self.layout.addWidget(MyBar(self))
        # create a horizontal layout to represent the tab bar
        self.tabLayout = QHBoxLayout()
        self.tabLayout.addStretch(-1)
        # left, top, right, bottom
        # pad the left and right so we can still resize from that location
        self.tabLayout.setContentsMargins(MARGIN,0,MARGIN,0)
        # add the tab bar to the vertical layout
        self.layout.addLayout(self.tabLayout)     
        # set the layout
        self.setLayout(self.layout)
        # add the initial default tab that will open on launch
        self.newTabEmpty()
        # make the default size be half the window
        self.setGeometry(startingLocation[0], startingLocation[1], startingLocation[0], startingLocation[1])
        #self.layout.setContentsMargins(MARGIN,0,MARGIN,MARGIN)
        self.layout.setContentsMargins(0,0,0,0)
        # the min height will be 600 x 600
        self.setMinimumSize(600, 600)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.pressing = False
        self.movingPosition = False
        self.resizingWindow = False
        self.start = QPoint(0, 0)
        self.setStyleSheet("""
            background-color: #4C566A; 
                          """)
        # flags for starting location of resizing window
        self.left = False
        self.right = False
        self.bottom = False
        self.top = False
        self.bl = False
        self.br = False
        self.setMouseTracking(True)
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
        self.shortcut_closeTab.activated.connect(self.closeTab)

        self.shortcut_openFile = QShortcut(QKeySequence('Ctrl+o'), self)
        self.shortcut_openFile.activated.connect(self.openFile)

        self.shortcut_saveFile = QShortcut(QKeySequence('Ctrl+s'), self)
        self.shortcut_saveFile.activated.connect(self.saveFile)

        # highlight thecurrent line
        textBoxArr[currentActiveTextBox].cursorPositionChanged.connect(self.posish)
    
    def posish(self):
        print("hi")

    def setSavedToFalse(self):
        tabArr[currentActiveTextBox].isSaved = False

    def saveFile(self):
        global currentActiveTextBox
        # detect if there was a change in the active text edit, and if so change the corresponding
        # tab's isSaved to False
        textBoxArr[currentActiveTextBox].textChanged.connect(self.setSavedToFalse)
        
        # only save if there have been no changes
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
                    f.write(textBoxArr[curTab].toPlainText())
                    # set the isSaved indicator to True
                    tabArr[curTab].isSaved = True
                    # store the tab we want to land on
                    tempTab = tabArr[curTab]
                    # finally close the current active tab
                    self.closeTab()
                    # now move to the tab we were on
                    tempTab.tabClicked()
                else:
                    f.write(textBoxArr[currentActiveTextBox].toPlainText())
                    tabArr[currentActiveTextBox].isSaved = True
                    # click on it so that the title of the window changes to match the tab
                    tabArr[currentActiveTextBox].tabClicked()
                f.close()

    def openFile(self):
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
                print(finalName)
                # create a new tab with the name of the file that was opened
                self.newTab(finalName, aTuple[0], content)
    
    def popup_clicked(self, i):
        print("hello")

    def closeTab(self):
        global currentActiveTextBox
        # for storing closed tabs to be able to restore them
        global tabStack
        okayToClose = False
        isCancelled = False
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
            
        if isCancelled == False:    
            # close tab and textbox at currentactivetextbox
            if len(tabArr) > 1 and okayToClose:
                self.layout.itemAt(textBoxIndex).widget().removeWidget(textBoxArr[currentActiveTextBox])
                # remove the tab from the tab bar
                self.tabLayout.removeWidget(tabArr[currentActiveTextBox])
                # remove the tab from the tab array
                tabArr.remove(tabArr[currentActiveTextBox])
                # remove the textbox from the array
                textBoxArr.remove(textBoxArr[currentActiveTextBox])

                # if we removed the last tab close the program
                if len(tabArr) == 0:
                    self.close()
                
                # if the tab we just removed is the first tab
                if currentActiveTextBox == 0:
                    # just shift over to the tab to its right by staying at index 0
                    tabArr[currentActiveTextBox].tabClicked()

                # if we just removed the last tab
                elif currentActiveTextBox == len(tabArr):
                    # we just shift over to the left
                    print(currentActiveTextBox)
                    tabArr[currentActiveTextBox - 1].tabClicked()
                    print(currentActiveTextBox)
                
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
        # if we are not already displaing this tab
        #if mainWin.layout.itemAt(textBoxIndex).widget().currentWidget() != textBoxArr[index]:
        global currentActiveTextBox
        currentActiveTextBox = index
        mainWin.layout.itemAt(textBoxIndex).widget().setCurrentWidget(textBoxArr[index])
        mainWin.layout.itemAt(textBoxIndex).widget().currentWidget().setFocus()
        print("current active text box = ", currentActiveTextBox)

    # add a new textbox to go along with this tab making this tab the parent of that textbox
    def addTextBox(self, contents):  
        global textBoxArr
        global currentActiveTextBox
        #first create the new textbox widget
        textbox = QPlainTextEdit(mainWin)
        textbox.setStyleSheet("""
            border: none;
            font: 14pt "Consolas";
            color: #D8DEE9;
            selection-color: #4C566A;
            selection-background-color: #D8DEE9;
                                """)
        textbox.resize(mainWin.width() - 100, mainWin.height() - 100)
        textbox.move(0,0)
        textbox.setLineWrapMode(textbox.WidgetWidth)
        textbox.setCursorWidth(3)
        textbox.setTabStopWidth(textbox.fontMetrics().width(' ') * TAB_SIZE)
        #------------------------------------------------------------------------#
        font = QFont()
        font.setFamily("Consolas")
        font.setFixedPitch( True )
        font.setPointSize( 14 )
        textbox.setFont( font )
        #------------------------------------------------------------------------#
        # add the contents of the file to the textbox
        textbox.setPlainText(contents)
        textBoxArr.append(textbox)
        # check if there is a stack of text boxes yet
        # if not then there should only be the title adn tab bar
        if mainWin.layout.count() == 2:
            # create the stack of textbox widgets
            stack = QStackedWidget(mainWin)
            stack.addWidget(textbox)
            mainWin.layout.addWidget(stack)
            stack.setContentsMargins(START_INDENT,0,5,5)
            stack.setMouseTracking(True)
        # if the stack is already created then we place the textbox on the stack
        else:
            mainWin.layout.itemAt(textBoxIndex).widget().addWidget(textbox)
        # make the textbox we just added the current widget
        mainWin.layout.itemAt(textBoxIndex).widget().setCurrentWidget(textbox)
        # save the current active text box
        currentActiveTextBox = len(textBoxArr) - 1
        print("current active text box = ", currentActiveTextBox)
        # focus the cursor on the new text box
        textbox.setFocus()

    def newTab(self, name, filePath, contents):
        global tabCount
        global tabArr
        tab = Tab(name, filePath)
        tabArr.append(tab)
        mainWin.tabLayout.insertWidget(tabCount, tab)
        tabCount += 1
        self.addTextBox(contents)

    def newTabEmpty(self):
        global tabCount
        global tabArr
        tab = Tab("", "")
        tabArr.append(tab)
        mainWin.tabLayout.insertWidget(tabCount, tab)
        tabCount += 1
        self.addTextBox("")

    def on_focusChanged(self):
        global focused
        focused = self.isActiveWindow()

    def mousePressEvent(self, event):
        pos = event.pos()
        # set pressing to true
        self.pressing = True
        # if they clicked on the edge then we need to change pressing to true and resizingWindow to
        # true and we need to change the cursor shape
        if pos.y() >= self.height() - 8 and pos.x() <= 8 and pos.y() > 8:
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
        if self.pressing:
            QApplication.setOverrideCursor(Qt.ArrowCursor)
        # bottom left
        elif pos.y() >= self.height() - 5 and pos.x() <= 5 and pos.y() > 5:
            QApplication.setOverrideCursor(Qt.SizeBDiagCursor)
        # bottom right
        elif pos.x() >= self.width() - 5 and pos.y() >= self.height() - 5:
            QApplication.setOverrideCursor(Qt.SizeFDiagCursor)
        # bottom
        elif pos.x() > 5 and pos.x() < self.width() - 5 and pos.y() >= self.height() - 5:
            QApplication.setOverrideCursor(Qt.SizeVerCursor)
        # left
        elif pos.x() <= 5 and pos.y() > 5:
            QApplication.setOverrideCursor(Qt.SizeHorCursor)
        # right
        elif pos.x() >= self.width() - 5 and pos.y() > 5:
            QApplication.setOverrideCursor(Qt.SizeHorCursor)
        else:
            if self.pressing == False:
                QApplication.setOverrideCursor(Qt.ArrowCursor)
        # if they are resizing
        # need to subtract the movement from the width/height 
        # but I also need to account for if they are resizing horizontally from the left or
        # vertically from the top because I need to shift the window to the right/down the same amount
        if self.pressing and self.resizingWindow:
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
    
    def tabLeft(self):
        print("here")
        self.displayTextBox(currentActiveTextBox - 1)

class MyBar(QWidget):
    def __init__(self, parent):
        super(MyBar, self).__init__()
        global titleBar
        titleBar = self
        # make the main window the parent
        self.parent = parent
        # create the layout to store the titlebar and buttons horizontally
        self.layout = QHBoxLayout()
        # allow for 8 pixels at the right so we can resize right and top right
        # also 8 margin at the top so that the buttons don't get in the way of resizing
        # left, top, right, bottom
        self.layout.setContentsMargins(0,5,0,0)
        self.layout.setSpacing(0)
        self.title = QLabel("test.py" + " - notes app")
        self.title.setMouseTracking(True)
        
        btn_size = 35

        self.btn_close = QPushButton("x")
        self.btn_close.clicked.connect(self.btn_close_clicked)
        # make the corner buttons more rectangular in the horizontal way
        self.btn_close.setFixedSize(btn_size+25,btn_size)
        self.btn_close.setStyleSheet("""
            QPushButton
            {
            background-color: #4C566A; 
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
            background-color: #4C566A; 
            border:none;
            color: #E5E9F0;
            font: 14pt "Consolas";
            }
            QPushButton::hover
            {
                background-color : #D8DEE9;
                color: #4C566A
            }
                                """)
        self.btn_min.setMouseTracking(True)
        self.btn_max = QPushButton("+")
        self.btn_max.clicked.connect(self.btn_max_clicked)
        self.btn_max.setFixedSize(btn_size+25, btn_size)
        self.btn_max.setStyleSheet("""
            QPushButton
            {
            background-color: #4C566A; 
            border:none;
            color: #E5E9F0;
            font: 14pt "Consolas";
            }
            QPushButton::hover
            {
                background-color : #D8DEE9;
                color: #4C566A
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
            background-color: #4C566A;
            color: #E5E9F0;
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

    def btn_min_clicked(self):
        # same with the show minimized
        self.parent.showMinimized()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            return
        pos = event.pos()
        self.pressing = True
        if pos.x() <= 8 or pos.x() >= self.parent.width() - 8 or pos.y() <= 8:
            self.resizingWindow = True
            # top left
            if pos.x() <= 8 and pos.y() <= 8:
                self.start = event.pos()
                self.tl = True
            # top right
            elif pos.x() >= self.width() - 8 and pos.y() <= 8:
                self.resizingWindow = True
                self.start = event.pos()
                self.tr = True
            # top
            elif pos.y() <= 8 and pos.x() > 8 and pos.x() < self.width() - 8:
                self.start = event.pos().y()
                self.top = True     
            # left
            elif pos.x() <= 8 and pos.y() > 8:
                self.start = event.pos().x()
                self.left = True   
            # right
            elif pos.x() >= self.width() - 8 and pos.y() > 8:
                self.start = event.pos().x()
                self.right = True    
        else:
            self.movingPosition = True
            self.start = self.mapToGlobal(event.pos())

    def mouseMoveEvent(self, event):
        pos = event.pos()
        if self.pressing:
            QApplication.setOverrideCursor(Qt.ArrowCursor)
        # top left
        elif pos.x() <= 5 and pos.y() <= 5:
            QApplication.setOverrideCursor(Qt.SizeFDiagCursor)
        # top right
        elif pos.x() >= self.width() - 5 and pos.y() <= 5:
            QApplication.setOverrideCursor(Qt.SizeBDiagCursor)
        # top
        elif pos.y() <= 5 and pos.x() > 5 and pos.x() < self.width() - 5:
            QApplication.setOverrideCursor(Qt.SizeVerCursor)
        # left
        elif pos.x() <= 5 and pos.y() > 5:
            QApplication.setOverrideCursor(Qt.SizeHorCursor)
        # right
        elif pos.x() >= self.width() - 5 and pos.y() > 5:
            QApplication.setOverrideCursor(Qt.SizeHorCursor)
        else:
            if self.pressing == False:
                QApplication.setOverrideCursor(Qt.ArrowCursor)

        if self.pressing and self.movingPosition:
            self.end = self.mapToGlobal(event.pos())
            self.movement = self.end-self.start
            self.parent.setGeometry(self.mapToGlobal(self.movement).x(),
                                self.mapToGlobal(self.movement).y(),
                                self.parent.width(),
                                self.parent.height())
            self.start = self.end
    
        elif self.resizingWindow == True and self.pressing == True:
            # resize from the top
            if self.top == True:
                # resize from the top
                if self.parent.height() - event.pos().y() >= 600:
                    self.parent.setGeometry(self.parent.pos().x(), self.parent.pos().y() + event.pos().y(), self.parent.width(), self.parent.height() - event.pos().y())
            # resize from the left to the right
            if self.left == True:
                # resize from the left
                if self.parent.width() - event.pos().x() >= 600:
                    self.parent.setGeometry(self.parent.pos().x() + event.pos().x(), self.parent.pos().y(), self.parent.width() - event.pos().x(), self.parent.height())
            # resize from the top left
            if self.tl == True:
                # move both dimensions if both boundaries are okay
                if self.parent.width() - event.pos().x() >= 600 and self.parent.height() - event.pos().y() >= 600:
                    self.parent.setGeometry(self.parent.pos().x() + event.pos().x(), self.parent.pos().y() + event.pos().y(), self.parent.width() - event.pos().x(), self.parent.height() - event.pos().y())
                # move only top if width is already at its smallest
                elif self.parent.height() - event.pos().y() >= 600:
                    self.parent.setGeometry(self.parent.pos().x(), self.parent.pos().y() + event.pos().y(), self.parent.width(), self.parent.height() - event.pos().y())
                # move only left if height is at its smallest
                elif self.parent.width() - event.pos().x() > 600:
                    self.parent.setGeometry(self.parent.pos().x() + event.pos().x(), self.parent.pos().y(), self.parent.width() - event.pos().x(), self.parent.height())
            # resize from the right
            if self.right == True:
                pos = event.pos().x()
                if self.parent.width() >= 600:
                    self.parent.setGeometry(self.parent.pos().x(), self.parent.pos().y(), pos, self.parent.height()) 
            # resize top right
            if self.tr == True:
                pos = event.pos().x() 
                # top right
                if self.parent.height() - event.pos().y() >= 600 and self.parent.width() >= 600:
                    self.parent.setGeometry(self.parent.pos().x(), self.parent.pos().y() + event.pos().y(), pos, self.parent.height() - event.pos().y())

                # resize from the top
                elif self.parent.height() - event.pos().y() >= 600:
                    self.parent.setGeometry(self.parent.pos().x(), self.parent.pos().y() + event.pos().y(), self.parent.width(), self.parent.height() - event.pos().y())
                elif self.parent.width() >= 600:
                    self.parent.setGeometry(self.parent.pos().x(), self.parent.pos().y(), pos, self.parent.height()) 


    def mouseReleaseEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.RightButton:
            return
        self.pressing = False
        self.resizingWindow = False
        self.movingPosition = False
        self.top = False
        self.left = False
        self.tl = False
        self.right = False
        self.tr = False

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
# variable to track the main textbox index in case I update the layout order
textBoxIndex = 2
# variable to track the number of default tabs currently open
numEmptyTabs = 0
# variable to track the index of the tab so we know the textbox associated with it
tabCount = 0
# array storing the textboxes
textBoxArr = []
# arraf storing the tabs
tabArr = []
# variables to store the mainwindow and title bar
mainWin = 0
titleBar = 0
# index of current active textbox
currentActiveTextBox = -1
# if tabs cycling should wrap around
tabCycle = True
# stack to store closed tabs so we can reopen them
tabStack = []

if __name__ == "__main__":
    app = QApplication(sys.argv)
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
    mainWin.layout.itemAt(textBoxIndex).widget().currentWidget().setFocus()

    sys.exit(app.exec_())