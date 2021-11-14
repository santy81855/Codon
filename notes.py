import sys
from PyQt5 import QtCore
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget

class MyFilter(QObject):
    def eventFilter(self, obj, event):
        print(str((obj, event)))
        return False

class MainWindow(QWidget):

    def __init__(self):
        super(MainWindow, self).__init__()
        # set the opacity
        self.setWindowOpacity(1.0)
        self.layout = QVBoxLayout()
        self.layout.addWidget(MyBar(self))
        self.setLayout(self.layout)
        # make the default size be half the window
        self.setGeometry(startingLocation[0], startingLocation[1], startingLocation[0], startingLocation[1])
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.addStretch(-1)
        # the min height will be 100 x 100
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
        self.installEventFilter(MyFilter())
    
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
  
#SizeFDiagCursor
    def mouseMoveEvent(self, event):
        pos = event.pos()
        # bottom left
        if pos.y() >= self.height() - 8 and pos.x() <= 8 and pos.y() > 8:
            QApplication.setOverrideCursor(Qt.SizeBDiagCursor)
        # bottom right
        elif pos.x() >= self.width() - 8 and pos.y() >= self.height() - 8:
            QApplication.setOverrideCursor(Qt.SizeFDiagCursor)
        # bottom
        elif pos.x() > 8 and pos.x() < self.width() - 8 and pos.y() >= self.height() - 8:
            QApplication.setOverrideCursor(Qt.SizeVerCursor)
        # left
        elif pos.x() <= 8 and pos.y() > 8:
            QApplication.setOverrideCursor(Qt.SizeHorCursor)
        # right
        elif pos.x() >= self.width() - 8 and pos.y() > 8:
            QApplication.setOverrideCursor(Qt.SizeHorCursor)
        else:
            if self.pressing == False:
                QApplication.restoreOverrideCursor()
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
    def mouseReleaseEvent(self, QMouseEvent):
        self.pressing = False
        self.movingPosition = False
        self.resizingWindow = False
        self.left = False
        self.right = False
        self.bottom = False
        self.bl = False
        self.br = False

class MyBar(QWidget):

    def __init__(self, parent):
        super(MyBar, self).__init__()
        # make the main window the parent
        self.parent = parent
        # create the layout to store the titlebar and buttons horizontally
        self.layout = QHBoxLayout()
        # allow for 8 pixels at the right so we can resize right and top right
        # also 8 margin at the top so that the buttons don't get in the way of resizing
        self.layout.setContentsMargins(0,8,8,0)
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

    def resizeEvent(self, QResizeEvent):
        super(MyBar, self).resizeEvent(QResizeEvent)
        self.title.setFixedWidth(self.parent.width())

    # close the main window when the close button in the menu bar is pressed
    def btn_close_clicked(self):
        self.parent.close()

    def btn_max_clicked(self):
        # if the maximize button is pressed on the menubar, it should call the maximize function of
        # the parent window. It is a standard function, so it is not written in this code
        self.parent.showMaximized()

    def btn_min_clicked(self):
        # same with the show minimized
        self.parent.showMinimized()
    
    def mousePressEvent(self, event):
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
        # top left
        if pos.x() <= 8 and pos.y() <= 8:
            QApplication.setOverrideCursor(Qt.SizeFDiagCursor)
        # top right
        elif pos.x() >= self.width() - 8 and pos.y() <= 8:
            QApplication.setOverrideCursor(Qt.SizeBDiagCursor)
        # top
        elif pos.y() <= 8 and pos.x() > 8 and pos.x() < self.width() - 8:
            QApplication.setOverrideCursor(Qt.SizeVerCursor)
        # left
        elif pos.x() <= 8 and pos.y() > 8:
            QApplication.setOverrideCursor(Qt.SizeHorCursor)
        # right
        elif pos.x() >= self.width() - 8 and pos.y() > 8:
            QApplication.setOverrideCursor(Qt.SizeHorCursor)
        else:
            if self.pressing == False:
                QApplication.restoreOverrideCursor()

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
    sys.exit(app.exec_())