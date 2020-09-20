from PyQt5 import QtCore, uic, QtGui
from PyQt5 import QtWidgets
from functools import partial
import emojis
import sys
import os

ST = "background-color: #3a3d3d;\n"
"QPushButton {\n"
"color: white;\n"
"border: 1px solid #3a3d3d;\n"
"}"

class EmojiDialog(QtWidgets.QDialog):
    def __init__(self, window):
        super(EmojiDialog, self).__init__()
        self.window = window
        self.setWindowTitle("Emoji")
        uic.loadUi(os.path.join(os.path.abspath('gui'), 'dialogs', 'emoji', 'emoji.ui'), self)

        self.line_max = 5
        self.font = QtGui.QFont('Arial', 15)

        ## emoji db ##
        self.recent  = {}
        self.emoji_db = {'Recent': self.recent}
        self.tabs = {}

        for catg in emojis.db.get_categories():
            self.emoji_db[catg] = [emoji.emoji for emoji in emojis.db.get_emojis_by_category(catg)]
        #self.emoji_db['Recent'] = self.recent
        self.loadEmojis()

    def start(self):
        content, layout, _ = self.tabs['Recent']
        self.createEmoji(
            content,
            layout,
            sorted(
                self.recent,
                key = lambda i : self.recent.get(i)
            )
        )
        self.show()

    def addEmoji(self, emoji):
        if not self.recent.get(emoji):
            self.recent[emoji] = 0
        else:
            self.recent[emoji] += 1
        self.window.addEmoji(emoji)



    def createEmoji(self, content, layout, emojis):
        count = 4
        row = 1
        for value in emojis:
            if count == 4+self.line_max:
                count = 4
                row += 1
            button = QtWidgets.QPushButton(content)
            button.setText(value)
            button.setFont(self.font)
            button.clicked.connect(partial(
                self.addEmoji,
                value
            ))
            layout.addWidget(button, row, count, 1, 1)
            count += 1

    def loadEmojis(self, items :dict = None):
        items = items if items else self.emoji_db

        for emoji, values in items.items():
            tab = QtWidgets.QWidget()
            tab_layout = QtWidgets.QGridLayout(tab)
            scroll = QtWidgets.QScrollArea(tab)


            scroll.setStyleSheet(ST)
            scroll.setFrameShape(QtWidgets.QFrame.Box)
            scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
            scroll.setWidgetResizable(True)

            wcontents = QtWidgets.QWidget()
            wcontents.setGeometry(QtCore.QRect(0, 0, 424, 263))

            content_layout = QtWidgets.QGridLayout(wcontents)

            self.createEmoji(wcontents, content_layout, values)


            self.tabWidget.addTab(tab, emoji)
            self.tabs[emoji] = [wcontents, content_layout, tab]
            scroll.setWidget(wcontents)
            tab_layout.addWidget(scroll, 1, 1, 1, 1)

        for i in range(2):
            self.tabWidget.removeTab(0)
