from PyQt5 import QtWidgets
from PyQt5 import QtCore
from functools import partial, lru_cache
import typing
import copy

class Chat(object):
    def __init__(self, window, network):
        self.window = window
        self.network = network
        self.frames = []
        self.username = "guest"
        self.current_contact = None
        self.current_contact_uid = None
        self.window.chat_input.returnPressed.connect(self.addMsg)

    def addMsg(self, msg=None):
        if not msg:
            msg = self.window.chat_input.text()
            self.window.chat_input.setText("")
        if not msg.strip():
            return
        self.createMsg(msg, self.username, self.window.verticalLayout_10)

    def createMsg(self, text, author, layout):
        ## browser ##
        browser = QtWidgets.QTextBrowser(self.window.scrollAreaWidgetContents_2)
        browser.setMinimumSize(100, 100)
        browser.setMaximumSize(500, 100)
        browser.setStyleSheet("background-color: #009c99")
        browser.setText(text)

        ## button ##
        button = QtWidgets.QToolButton(self.window.scrollAreaWidgetContents_2)
        button.setMinimumSize(150, 25)
        button.setStyleSheet("background-color: #027573")
        button.setText(author)

        ## add to layout ##
        layout.addWidget(button)
        layout.addWidget(browser)
        layout.addWidget(QtWidgets.QLabel(self.window.scrollAreaWidgetContents_2))



    def clickedContact(self, contact : typing.Tuple[str, str]):
        uid, name = contact
        self.current_contact = name, self.current_contact_uid = uid
        msgs = self.network.data[uid]["msgs"]
        for msg in msgs:
            if msg["id"] in self.network.label_added:
                continue
            self.network.label_added.append(msg["id"])

            self.createMsg(msg["text"], msg["author"], self.window.verticalLayout_10)

    def getContactButtons(self, window, widget, contacts):
        for contact in contacts:
            b = QtWidgets.QPushButton(window)
            widget.addWidget(b)
            b.setText(contact.name)
            b.clicked.connect(partial(self.clickedContact, (contact.uid, contact.name)))
            self.network.button_values[contact.uid] = b
