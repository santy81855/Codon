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

class TextPreview(QPlainTextEdit):
    def __init__(self, parent):
        super(TextPreview, self).__init__()
        self.parent = parent
        self.setMouseTracking(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWordWrapMode(0)
    
    def getLastWord(self, cur):
        # store the position of the cursor
        position = cur.position()
        # select the word under the cursor
        cur.select(QTextCursor.WordUnderCursor)
        word = cur.selection().toPlainText()
        cur.clearSelection()
        cur.setPosition(position, QTextCursor.MoveAnchor)
        return word

    def setPlainText(self, text):
        global singleLineComment
        global multiLineComment
        global isStringSingle
        global isStringDouble
        #return QPlainTextEdit.setPlainText(self, text)
        # first it should clear the text box
        self.clear()
        # get the current filetype
        fileType = tabArr[currentActiveTextBox].getFileType()
        # if this is not a code file then there is no syntax highlighting anyway
        if fileType not in keywords:
            return QPlainTextEdit.setPlainText(self, text)
        # if it is a code file then we need to get the list of keywords to highlight
        list_of_keywords = keywords[fileType]
        # get the singlelinecomment character for this file type
        char = commentChar[fileType]
        isStringSingle = False
        isStringDouble = False
        multiLineComment = False
        singleLineComment = False     
        # add the text char by char while syntax highlighting it
        for c in text:
            # if we reach a space
            if c == ' ':
                # get the last word using the cursor
                cur = self.textCursor()
                position = cur.position()
                cur.select(QTextCursor.WordUnderCursor)
                word = cur.selection().toPlainText()
                # if the last word is a keyword
                if word in list_of_keywords:
                    if singleLineComment == False and multiLineComment == False and isStringSingle == False and isStringDouble == False:
                        temp = "<span style=\" font-size:3pt; font-weight:300; color:" + keywordColor + ";\" >" + word + "</span>"
                        cur.insertHtml(temp)
                       
                    elif singleLineComment == True or multiLineComment == True:
                        temp = "<span style=\" font-size:3pt; font-weight:300; color:" + commentColor + ";\" >" + word + "</span>"
                        cur.insertHtml(temp)
                    
                    elif isStringSingle == True or isStringDouble == True:
                        temp = "<span style=\" font-size:3pt; font-weight:300; color:" + stringColor + ";\" >" + word + "</span>"
                        cur.insertHtml(temp)
                        
                # if it is not a keyword leane it alone 
                else:
                    cur.clearSelection()
                    cur.setPosition(position, QTextCursor.MoveAnchor)
                # add the space 
                cur.insertText(c)
            # if we reach a newline
            elif c == '\n':
                cur = self.textCursor()
                singleLineComment = False
                cur.insertText('\n')
            # if we reach a python single line character
            elif fileType == "py" and c == "#":
                cur = self.textCursor()
                if isStringSingle == False and isStringDouble == False:
                    temp = "<span style=\" font-size:3pt; font-weight:300; color:" + commentColor + ";\" >#</span>"
                    cur.insertHtml(temp)
                    #singleLineComment = True
                else:
                    temp = "<span style=\" font-size:3pt; font-weight:300; color:" + stringColor + ";\" >#</span>"
                    cur.insertHtml(temp)
            
            elif fileType != "py" and c == '/':
                # get the character right before this one
                # check if this is the second slash
                cur = self.textCursor()
                position = cur.position()
                if position > 0 and isStringSingle == False and isStringDouble == False:
                    cur.setPosition(position, QTextCursor.MoveAnchor)
                    cur.setPosition(position - 1, QTextCursor.KeepAnchor)
                    char = cur.selection().toPlainText()
                    # if the character before this one is a slash then we know it's comment time so we
                    # replace the selection with 2 slashes
                    if char == '/':
                        comment = "<span style=\" font-size:3pt; font-weight:300; color:" + commentColor + ";\" >//</span>"
                        cur.insertHtml(comment)      
                        # set the single line comment to true
                        singleLineComment = True
                    # if the character before this one is a * then we have the end of a multiline comment
                    elif char == '*':
                        comment = "<span style=\" font-size:3pt; font-weight:300; color:" + commentColor + ";\" >*/</span>"
                        cur.insertHtml(comment)      
                        # set the single line comment to true
                        multiLineComment = True
                    # if it's just any random character before this then treat it like normal
                    else:
                        if singleLineComment == False and multiLineComment == False:
                            cur.clearSelection()
                            cur.setPosition(position, QTextCursor.MoveAnchor)
                            comment = "<span style=\" font-size:3pt; font-weight:300; color:" + textColor + ";\" >/</span>"
                            cur.insertHtml(comment)
                        else:      
                            cur.clearSelection()
                            cur.setPosition(position, QTextCursor.MoveAnchor)
                            comment = "<span style=\" font-size:3pt; font-weight:300; color:" + commentColor + ";\" >/</span>"
                            cur.insertHtml(comment)
                # if we are currently writing a string then make it string colored
                elif isStringSingle == True or isStringDouble == True:
                    comment = "<span style=\" font-size:3pt; font-weight:300; color:" + stringColor + ";\" >/</span>"
                    cur.insertHtml(comment)

                else:
                    if singleLineComment == False and multiLineComment == False:
                        comment = "<span style=\" font-size:3pt; font-weight:300; color:" + textColor + ";\" >/</span>"
                        cur.insertHtml(comment)             
                    else:
                        comment = "<span style=\" font-size:3pt; font-weight:300; color:" + commentColor + ";\" >/</span>"
                        cur.insertHtml(comment)    

            elif fileType != "py" and c == '*':
                cur = self.textCursor()
                position = cur.position()
                # need to check if the character before this one is a slash
                if position > 0 and isStringSingle == False and isStringDouble == False:
                    cur.setPosition(position, QTextCursor.MoveAnchor)
                    cur.setPosition(position - 1, QTextCursor.KeepAnchor)
                    char = cur.selection().toPlainText()
                    # if the character before this one is a slash then we know it's comment time so we
                    # replace the selection with 2 slashes
                    if char == '/':
                        comment = "<span style=\" font-size:3pt; font-weight:300; color:" + commentColor + ";\" >/*</span>"
                        cur.insertHtml(comment)      
                        # set the single line comment to true
                        multiLineComment = True
                   
                    # if it's just any random character before this then treat it like normal
                    else:
                        if singleLineComment == False and multiLineComment == False:
                            cur.clearSelection()
                            cur.setPosition(position, QTextCursor.MoveAnchor)
                            comment = "<span style=\" font-size:3pt; font-weight:300; color:" + keywordColor + ";\" >*</span>"
                            cur.insertHtml(comment)
                        else:      
                            cur.clearSelection()
                            cur.setPosition(position, QTextCursor.MoveAnchor)
                            comment = "<span style=\" font-size:3pt; font-weight:300; color:" + commentColor + ";\" >*</span>"
                            cur.insertHtml(comment)
                # if we are currently writing a string then make it string colored
                elif isStringSingle == True or isStringDouble == True:
                    comment = "<span style=\" font-size:3pt; font-weight:300; color:" + stringColor + ";\" >*</span>"
                    cur.insertHtml(comment)
                # if its the first char
                else:
                    if singleLineComment == False and multiLineComment == False:
                        comment = "<span style=\" font-size:3pt; font-weight:300; color:" + textColor + ";\" >/</span>"
                        cur.insertHtml(comment)             
                    else:
                        comment = "<span style=\" font-size:3pt; font-weight:300; color:" + commentColor + ";\" >/</span>"
                        cur.insertHtml(comment)  
            
            # if we get a string char
            elif c == "'":
                cur = self.textCursor()
                # if we are not in a comment or a string
                if multiLineComment == False and singleLineComment == False and isStringSingle == False and isStringDouble == False:
                    isStringSingle = True
                    comment = "<span style=\" font-size:3pt; font-weight:300; color:" + textColor + ";\" >'</span>"
                    cur.insertHtml(comment)  
                # if we are in a comment
                elif multiLineComment == True or singleLineComment == True:
                    comment = "<span style=\" font-size:3pt; font-weight:300; color:" + commentColor + ";\" >'</span>"
                    cur.insertHtml(comment)  
                # if we are in a double string
                elif isStringDouble == True:
                    comment = "<span style=\" font-size:3pt; font-weight:300; color:" + stringColor + ";\" >'</span>"
                    cur.insertHtml(comment)  
                # if we are ending a single string
                elif isStringSingle == True:
                    comment = "<span style=\" font-size:3pt; font-weight:300; color:" + textColor + ";\" >'</span>"
                    cur.insertHtml(comment)  
                    isStringSingle = False
            
            # insert tabs
            elif c == '\t':
                cur = self.textCursor()
                cur.insertText('\t')
            
            elif c == '"':
                cur = self.textCursor()
                # if we are not in a comment or a string
                if multiLineComment == False and singleLineComment == False and isStringSingle == False and isStringDouble == False:
                    isStringDouble = True
                    comment = "<span style=\" font-size:3pt; font-weight:300; color:" + textColor + ';\" >"</span>'
                    cur.insertHtml(comment)  
                # if we are in a comment
                elif multiLineComment == True or singleLineComment == True:
                    comment = "<span style=\" font-size:3pt; font-weight:300; color:" + commentColor + ';\" >"</span>'
                    cur.insertHtml(comment)  
                # if we are ending a double string
                elif isStringDouble == True:
                    comment = "<span style=\" font-size:3pt; font-weight:300; color:" + textColor + ';\" >"</span>'
                    cur.insertHtml(comment)  
                    isStringDouble = False
                # if we are in a singleString
                elif isStringSingle == True:
                    comment = "<span style=\" font-size:3pt; font-weight:300; color:" + stringColor + ';\" >"</span>'
                    cur.insertHtml(comment)
            
            # this means beginning of a function
            elif c == '(':
                cur = self.textCursor()
                # color the word before this functionColor if it is in any of the dictionaries
                word = self.getLastWord(cur)
                if singleLineComment == False and multiLineComment == False and isStringSingle == False and isStringDouble == False:
                    # highlight it 
                    cur.select(QTextCursor.WordUnderCursor)
                    newWord = "<span style=\" font-size:3pt; font-weight:300; color:" + functionColor + ";\" >" + word + "</span>"
                    cur.insertHtml(newWord)
                    cur.clearSelection()
                    # insert the ( using the paren color
                    openParen = "<span style=\" font-size:3pt; font-weight:300; color:" + parenColor + ";\" >(</span>"
                    cur.insertHtml(openParen)
                elif singleLineComment == True or multiLineComment == True:
                    # highlight it 
                    cur.select(QTextCursor.WordUnderCursor)
                    newWord = "<span style=\" font-size:3pt; font-weight:300; color:" + commentColor + ";\" >" + word + "</span>"
                    cur.insertHtml(newWord)
                    cur.clearSelection()
                    # insert the ( using the paren color
                    openParen = "<span style=\" font-size:3pt; font-weight:300; color:" + commentColor + ";\" >(</span>"
                    cur.insertHtml(openParen)
                elif isStringSingle == True or isStringDouble == True:
                    # highlight it 
                    cur.select(QTextCursor.WordUnderCursor)
                    newWord = "<span style=\" font-size:3pt; font-weight:300; color:" + stringColor + ";\" >" + word + "</span>"
                    cur.insertHtml(newWord)
                    cur.clearSelection()
                    # insert the ( using the paren color
                    openParen = "<span style=\" font-size:3pt; font-weight:300; color:" + stringColor + ";\" >(</span>"
                    cur.insertHtml(openParen)
            
            elif c == ')':
                cur = self.textCursor()
                word = self.getLastWord(cur)
                if singleLineComment == False and multiLineComment == False and isStringSingle == False and isStringDouble == False:
                    # insert the ) using the parenColor
                    closingParen = "<span style=\" font-size:3pt; font-weight:300; color:" + parenColor + ";\" >)</span>"
                    cur.insertHtml(closingParen)
                elif singleLineComment == True or multiLineComment == True:
                    # insert the ( using the paren color
                    openParen = "<span style=\" font-size:3pt; font-weight:300; color:" + commentColor + ";\" >)</span>"
                    cur.insertHtml(openParen)
                elif isStringSingle == True or isStringDouble == True:
                    # insert the ( using the paren color
                    openParen = "<span style=\" font-size:3pt; font-weight:300; color:" + stringColor + ";\" >)</span>"
                    cur.insertHtml(openParen)
            
            # all of these are the same color anyways            
            elif c == '{' or c == '}':
                cur = self.textCursor()
                word = self.getLastWord(cur)
                # if this is not a comment line we color it like normal
                if (singleLineComment == False and multiLineComment == False and isStringSingle == False and isStringDouble == False) or fileType == "py":
                    # insert the bracket using the bracketcolor
                    openingBracket = "<span style=\" font-size:3pt; font-weight:300; color:" + bracketColor + ";\" >" + c + "</span>"
                    cur.insertHtml(openingBracket)
                elif singleLineComment == True or multiLineComment == True:
                    openingBracket = "<span style=\" font-size:3pt; font-weight:300; color:" + commentColor + ";\" >" + c + "</span>"
                    cur.insertHtml(openingBracket)
                elif isStringSingle == True or isStringDouble == True:
                    openingBracket = "<span style=\" font-size:3pt; font-weight:300; color:" + stringColor + ";\" >" + c + "</span>"
                    cur.insertHtml(openingBracket)
            
            # all of these are the same color anyways            
            elif c == '[' or c == ']':
                cur = self.textCursor()
                word = self.getLastWord(cur)
                # if this is not a comment line we color it like normal
                if singleLineComment == False and multiLineComment == False and isStringSingle == False and isStringDouble == False:
                    # insert the bracket using the bracketcolor
                    openingBracket = "<span style=\" font-size:3pt; font-weight:300; color:" + braceColor + ";\" >" + c + "</span>"
                    cur.insertHtml(openingBracket)
                elif singleLineComment == True or multiLineComment == True:
                    openingBracket = "<span style=\" font-size:3pt; font-weight:300; color:" + commentColor + ";\" >" + c + "</span>"
                    cur.insertHtml(openingBracket)
                elif isStringSingle == True or isStringDouble == True:
                    openingBracket = "<span style=\" font-size:3pt; font-weight:300; color:" + stringColor + ";\" >" + c + "</span>"
                    cur.insertHtml(openingBracket)
            
            # if it is a number
            elif c in numbersList:
                # just make sure that there is not an alpha character right before it
                cur = self.textCursor()
                position = cur.position()
                isNumber = True
                if position > 0:
                    # select the character right before it
                    cur.setPosition(position, QTextCursor.MoveAnchor)
                    cur.setPosition(position - 1, QTextCursor.KeepAnchor)
                    char = cur.selection().toPlainText()

                    if char.isalpha() == True:
                        isNumber = False
                cur.clearSelection()
                cur.setPosition(position, QTextCursor.MoveAnchor)
                if singleLineComment == False and multiLineComment == False and isStringSingle == False and isStringDouble == False:
                    if isNumber == True:
                        temp = "<span style=\" font-size:3pt; font-weight:300; color:" + numberColor + ";\" >" + c + "</span>"
                        cur.insertHtml(temp)
                    else:
                        temp = "<span style=\" font-size:3pt; font-weight:300; color:" + textColor + ";\" >" + c + "</span>"
                        cur.insertHtml(temp)
                elif singleLineComment == True or multiLineComment == True:
                    temp = "<span style=\" font-size:3pt; font-weight:300; color:" + commentColor + ";\" >" + c + "</span>"
                    cur.insertHtml(temp)
                elif isStringSingle == True or isStringDouble == True:
                    temp = "<span style=\" font-size:3pt; font-weight:300; color:" + stringColor + ";\" >" + c + "</span>"
                    cur.insertHtml(temp)

            else:
                cur = self.textCursor()
                position = cur.position()
                # if its just normal text 
                if singleLineComment == False and multiLineComment == False and isStringSingle == False and isStringDouble == False:
                    comment = "<span style=\" font-size:3pt; font-weight:300; color:" + textColor + ";\" >" + c + "</span>"
                    cur.insertHtml(comment)    
                # if it is part of a comment
                elif singleLineComment == True or multiLineComment == True:
                    comment = "<span style=\" font-size:3pt; font-weight:300; color:" + commentColor + ";\" >" + c + "</span>"
                    cur.insertHtml(comment)    
                # if it is part of a string
                elif isStringSingle == True or isStringDouble == True:
                    comment = "<span style=\" font-size:3pt; font-weight:300; color:" + stringColor + ";\" >" + c + "</span>"
                    cur.insertHtml(comment) 
