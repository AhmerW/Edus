from PyQt5 import QtWidgets, QtCore, sip, QtGui
from functools import partial, lru_cache
from datetime import datetime, date
from time import time as timestamp
import threading
import typing
from lib.security.gen import randUid

MAX_MSG = 20

class Chat(object):
    def __init__(self, window, network):
        self.window = window
        self.network = network
        self.frames = {}
        self.username = "guest"
        self.uid = "self"



        self.window.chat_input.returnPressed.connect(self.addMsg)
        self.window.msg_left.setAlignment(QtCore.Qt.AlignLeft)
        self.window.msg_right.setAlignment(QtCore.Qt.AlignRight)


        self.current_contact = None
        self.current_contact_uid = None
        self.layout_dic = {0: self.window.msg_left, 1: self.window.msg_right}

    def reply(self, uid):
        username = self.network.getUbu(uid)
        if uid == self.uid or not username:
            return
        self.window.chat_input.setText("@{0} ".format(username))

    def getDate(self, d1):
        d1, d2 = datetime.fromtimestamp(timestamp()), datetime.fromtimestamp(d1)
        dif = d1 - d2
        if dif.days == 0:
            d = "today"
        elif dif.days == -1:
            d = "yesterday"
        else:
            d = "{0} days ago".format(dif.days)
        return "{0} at {1}".format(d, "{0}:{1}".format(d2.hour, d2.minute))


    def addMsg(self, msg=None, username=None, uid=None, db=True, from_self=True):
        username = username if username else self.username
        uid = uid if uid else self.uid
        if not msg:
            msg = self.window.chat_input.text()
            self.window.chat_input.setText("")

        if not msg.strip():
            return
        if db:
            if len(self.network.data[self.current_contact_uid]["msgs"]) >= MAX_MSG:
                self.network.data[self.current_contact_uid]["msgs"].clear()
            data = {'author': self.username, 'author_id': self.uid, 'text': msg, 'id': randUid(12), 'date': timestamp()}
            self.network.data[self.current_contact_uid]["msgs"].append(data)

        self.createEmpty(self.layout_dic[not from_self])
        self.createMsg(msg, username, uid, int(timestamp()), self.layout_dic[from_self])

    def createMsg(self, text, author, author_id, date, msg_layout):


        ## text frame ##
        textframe = QtWidgets.QFrame(self.window.scrollAreaWidgetContents_3)
        textframe.setMaximumSize(QtCore.QSize(300, 150))
        textframe.setStyleSheet("background-color: #009c99")
        textframe.setFrameShape(QtWidgets.QFrame.StyledPanel)
        textframe.setFrameShadow(QtWidgets.QFrame.Raised)
        textframe.setObjectName("textframe")

        layout = QtWidgets.QVBoxLayout(textframe)
        layout.setObjectName("verticalLayout_10")

        ## author and date buton ##
        button = QtWidgets.QToolButton(textframe)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(button.sizePolicy().hasHeightForWidth())
        button.setSizePolicy(sizePolicy)
        button.setStyleSheet("border: 1px solid #009c99")
        button.setObjectName("toolButton")
        layout.addWidget(button)

        ## text browser ##
        browser = QtWidgets.QTextBrowser(textframe)
        browser.setObjectName("textBrowser")
        layout.addWidget(browser)

        ## reply button ##
        reply_button = QtWidgets.QToolButton(textframe)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(reply_button.sizePolicy().hasHeightForWidth())
        reply_button.setSizePolicy(sizePolicy)
        reply_button.setMaximumSize(QtCore.QSize(16777215, 20))
        reply_button.setLayoutDirection(QtCore.Qt.LeftToRight)
        reply_button.setStyleSheet("background-color: #007a78; border: 1px solid #007a78;")

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("assets/icons/reply.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        reply_button.setIcon(icon)
        reply_button.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)

        ## label ##
        label = QtWidgets.QLabel(self.window.scrollAreaWidgetContents_3)
        label.setMinimumSize(30, 30)

        ## set text ##
        browser.setText(text)
        button.setText("By {0}    {1}".format(author, self.getDate(date)))
        reply_button.setText("reply")
        reply_button.clicked.connect(partial(self.reply, author_id))

        ## add to layout ##
        layout.addWidget(reply_button)

        msg_layout.addWidget(label)
        msg_layout.addWidget(textframe)
        self.window.scrollArea_3.scroll(50, 50)
        self.window.scrollArea_3.verticalScrollBar().setValue(self.window.scrollArea_3.verticalScrollBar().maximum())



    def createEmpty(self, layout):
        label = QtWidgets.QLabel(self.window.scrollchat_frame)
        label.setMinimumSize(300, 150)
        layout.addWidget(label)

    def deleteCurrent(self, layout):
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().setParent(None)

    def getLayouts(self, uid):
        if uid in self.frames:
            return self.frames[uid]
        return self.window.scrollchat_frame, self.window.msg_left, self.window.msg_right


    def clickedContact(self, contact : typing.Tuple[str, str]):
        uid, name = contact

        self.current_contact = name
        self.current_contact_uid = uid

        self.deleteCurrent(self.window.msg_left)
        self.deleteCurrent(self.window.msg_right)

        for msg in self.network.data[uid]["msgs"]:
            self.network.label_added.append(msg["id"])
            if msg["author_id"] == self.uid:
                self.createMsg(msg["text"], "{0} ({1})".format(self.username, 'you'), msg["author_id"], msg["date"], self.window.msg_right)
                self.createEmpty(self.window.msg_left)

            else:
                self.createMsg(msg["text"], msg["author"], msg["author_id"], msg["date"], self.window.msg_left)
                self.createEmpty(self.window.msg_right)

    def getContactButtons(self, window, widget, contacts):
        for contact in contacts:
            b = QtWidgets.QPushButton(window)
            widget.addWidget(b)
            b.setText(contact.name)
            b.clicked.connect(partial(self.clickedContact, (contact.uid, contact.name)))
            self.network.button_values[contact.uid] = b