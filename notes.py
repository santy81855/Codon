import sys
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtGui import QCursor, QMouseEvent, QFont, QKeySequence
from PyQt5.QtCore import QPoint, pyqtSignal
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QObject, QMimeData
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QCompleter
from PyQt5.QtWidgets import QHBoxLayout, QTextEdit, QPlainTextEdit
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget
import textwrap
from pynput import keyboard
import string

class Tab(QWidget):
    def __init__(self, fileName):
        super(Tab, self).__init__()
        global numEmptyTabs
        self.fileName = ""
        self.fileLocation = ""
        if fileName == "":
            self.fileName = "untitled_" + str(numEmptyTabs + 1) + ".txt"
            numEmptyTabs += 1
        else:
            self.fileName = fileName
        # create a layout that can store the tab and its close button
        self.singleTabLayout = QHBoxLayout()
        # create a button to represent the file
        self.tabButton = QPushButton(self.fileName)
        self.tabButton.setMouseTracking(True)
        self.tabButton.clicked.connect(self.tabClicked)
        self.tabButton.setFixedSize(200, 40)
        self.tabButton.setStyleSheet("""
            QPushButton
            {
            background-color: #4C566A;
            color: #D8DEE9;
            font: 14pt "Consolas";
            border: none;
            }
            QPushButton::hover
            {
            background-color: #D8DEE9;
            color: #4C566A;
            border: none;
            }
                                    """)
        self.setMouseTracking(True)
        self.singleTabLayout.addWidget(self.tabButton)
        self.setLayout(self.singleTabLayout)
        # left, top, right, bottom
        self.singleTabLayout.setContentsMargins(0,0,0,0)        

    def tabClicked(self):
        # when we click the tab, we want to focus the tab by changing its color to be the same as
        # the background
        self.tabButton.setStyleSheet("""
            QPushButton
            {
            background-color: #D8DEE9;
            color: #4C566A;
            font: 14pt "Consolas";
            border: none;
            }
            QPushButton::hover
            {
            background-color: #4C566A;
            color: #D8DEE9;
            border: none;
            }-  
                                    """)
        # this is where I need to put the code to replace text currently in the textbox with text
        # from the file on the tab that was clicked
        for i in range(0, len(tabArr)):
            # if we find the right tab we know which textbox to display
            if tabArr[i] == self:
                displayTextBox(i)

def displayTextBox(index):
    # if we are not already displaing this tab
    if mainWin.layout.itemAt(textBoxIndex).widget() != textBoxArr[index]:
        mainWin.layout.removeItem(mainWin.layout.itemAt(textBoxIndex))
        mainWin.layout.addWidget(textBoxArr[index])


# add a new textbox to go along with this tab making this tab the parent of that textbox
def addTextBox():    
    global textBoxArr
    textWidget = TextField(mainWin)
    # if there is no textbox yet (when we are creating the mainwindow for the first time)
    if len(textBoxArr) == 0:
        mainWin.layout.addWidget(textWidget)
        # add this widget to the array of textboxes
        textBoxArr.append(textWidget)            
    # if there is already a textbox then we remove it and replace it
    else:
        mainWin.layout.removeItem(mainWin.layout.itemAt(textBoxIndex))
        mainWin.layout.addWidget(textWidget)

def newTab(name):
    global tabCount
    global tabArr
    tab = Tab(name)
    tabArr.append(tab)
    mainWin.tabLayout.insertWidget(tabCount, tab)
    tabCount += 1
    addTextBox()

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        # store the main window widget
        global mainWin
        global tabCount
        mainWin = self
        # set the opacity
        self.setWindowOpacity(0.8)
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
        # add the initial default tab that will open on launch
        newTab("")
        newTab("")
        #self.tabLayout.setSpacing(0)
           
        # add the initial textbox for the default tab
        #addTextBox()        
        #self.layout.addStretch(-1)
        self.setLayout(self.layout)
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

    def on_focusChanged(self):
        global focused
        focused = self.isActiveWindow()
        if focused:
            self.layout.itemAt(textBoxIndex).widget().textbox.setFocus()

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
    
    def keyPressEvent(self, event):
        QApplication.setOverrideCursor(Qt.IBeamCursor)

class TextField(QWidget):
    def __init__(self, parent):
        super(TextField, self).__init__()
        self.parent = parent
        # need a layout that will allow for vertical numbering on the left
        self.vertLayout = QVBoxLayout()
        self.vertLayout.setContentsMargins(0,0,0,0)
        
        self.layout = QVBoxLayout()
        # left, top, right, bottom
        self.layout.setContentsMargins(25,0,MARGIN,MARGIN)
        self.layout.setSpacing(0)
        self.textbox = QPlainTextEdit(self)
        self.textbox.setStyleSheet("""
            border: none;
            font: 14pt "Consolas";
            color: #D8DEE9;
            selection-color: #4C566A;
            selection-background-color: #D8DEE9;
                                """)
        self.textbox.resize(self.parent.width() - 100, self.parent.height() - 100)
        self.textbox.move(0,0)
        #self.textbox.setReadOnly(True)
        #self.textbox.ensureCursorVisible()
        self.textbox.setLineWrapMode(self.textbox.WidgetWidth)
        #self.textbox.acceptRichText()
        self.layout.addWidget(self.textbox)
        self.setLayout(self.layout)
        self.setMouseTracking(True)
        self.textbox.setCursorWidth(3)
        self.textbox.setTabStopWidth(self.textbox.fontMetrics().width(' ') * TAB_SIZE)

    def keyPressEvent(self, event):
        QApplication.setOverrideCursor(Qt.IBeamCursor)

class MyBar(QWidget):
    def __init__(self, parent):
        super(MyBar, self).__init__()
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

def printStack():
    SHIFT = "Key.shift"
    ENTER = "Key.enter"
    SPACE = 'Key.space'
    '''
    for i in range(0, len(stack) - 1):
        if stack[i][0] == SPACE:
            print(" ")
        else:
            print(stack[i][0])
    '''

def on_press(key):
    global stack
    global isControlDown
    if focused:
        # convert keycode to normal string
        letter = str(key).replace("'", "")
        letter = letter.replace("Key.", "")
        if "enter" in letter or letter == 'A':
            addTab("hello")
        if letter == 'ctrl_l' or letter == 'ctrl_r':
            isControlDown = True
        if isControlDown:
            print(letter)
            if "x13" in letter:
                print("save instead of storing teh s")
        else:
            stack.append(letter)
        print(stack)

def on_release(key):
    global stack
    global isControlDown
    if focused:
        # convert keycode to normal string
        letter = str(key).replace("'", "")
        letter = letter.replace("Key.", "")
        if letter == "ctrl_l" or letter == "ctrl_r":
            isControlDown = False
        try:
            k = key.char
        except:
            k = key.name

        #print(letter)
        #stack.append(letter)

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
# tab size
TAB_SIZE = 4
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
# variables to store the mainwindow and tab bar
mainWin = 0
tabWin = 0

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
    mw.layout.itemAt(textBoxIndex).widget().textbox.setFocus()
    # get text through python
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    sys.exit(app.exec_())