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
wordCountIndex = 3
# language selection index
languageSelectionIndex = 2
# cursor position button index
cursorPositionIndex = 0
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
mainWin = None
titleBar = None
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
keywordColor = "#81A1C1"
parenColor = "#EBCB8B"
braceColor = "#D08770"
functionColor = "#88C0D0"
commentColor = "#4C566A"
textColor = "#D8DEE9"
stringColor = "#8FBCBB"
numberColor = "#BF616A"
backgroundColor = "#2E3440"
lineNumberColor = "#8FBCBB"
selectionColor = "#4C566A"
curLineColor = "#3B4252"
selectionTextColor = "#D8DEE9"
classColor = "#A3BE8C"
operatorColor = "#EBCB8B"
# create a dictionary to convert from shorthand to full formatted name
keywords = {}
keywords["py"] = "    python"
keywords["c"] = "         c"
keywords["cpp"] = "       cpp"
keywords["java"] = "      java"
keywords["js"] = "javascript"
keywords["cs"] = "        c#"
keywords["json"] = "      json"

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

# dictionary to convert from language name to shorthand
languageDict = {}
languageDict["python"] = "py"
languageDict["c"] = "c"
languageDict["c#"] = "cs"
languageDict["c++"] = "cpp"
languageDict["java"] = "java"
languageDict["javascript"] = "js"
languageDict["json"] = "json"
languageDict["plaintext"] = None