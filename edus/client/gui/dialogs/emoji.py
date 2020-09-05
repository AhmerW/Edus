from PyQt5 import QtWidgets
from PyQt5 import QtCore, uic, QtGui
from functools import partial
import emojis
import sys
import os

ST = "background-color: gray;\n"
"QPushButton {\n"
"color: white;\n"
"border: 1px solid black;\n"
"}"

class EmojiDialog(QtWidgets.QDialog):
    def __init__(self, window):
        super(EmojiDialog, self).__init__()
        self.window = window
        uic.loadUi(os.path.join(os.path.abspath('gui'), 'dialogs', 'emoji.ui'), self)

        self.line_max = 5

        ## emoji db ##
        self.recent  = []
        self.emoji_db = {}
        
        for catg in emojis.db.get_categories():
            self.emoji_db[catg] = [emoji.emoji for emoji in emojis.db.get_emojis_by_category(catg)]
        self.loadEmojis()
    def loadEmojis(self):
        for emoji, values in self.emoji_db.items():
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

            count = 4
            row = 1
            for value in values:
                if count == 4+self.line_max:
                    count = 4
                    row += 1
                button = QtWidgets.QPushButton(wcontents)
                button.setText(value)
                button.clicked.connect(partial(
                    self.window.addEmoji,
                    value
                ))
                content_layout.addWidget(button, row, count, 1, 1)
                count += 1

            self.tabWidget.addTab(tab, emoji)
            scroll.setWidget(wcontents)
            tab_layout.addWidget(scroll, 1, 1, 1, 1)

        for i in range(2):
            self.tabWidget.removeTab(0)
