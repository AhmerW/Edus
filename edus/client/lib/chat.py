from PyQt5 import QtWidgets, QtCore, sip, QtGui
from functools import partial, lru_cache
from datetime import datetime, date
from time import time as timestamp
import threading
import typing
import emojis
from lib.security.gen import randUid
from gui.dialogs.emoji.emoji import EmojiDialog

MAX_MSG = 20

class Chat(object):
    def __init__(self, window, network, apic, loop):
        self.window = window
        self.network = network
        self.apic = apic
        self.loop = loop
        self.frames = {}
        self.username = "guest"
        self.uid = "self"
        self.dialog_emoji = EmojiDialog(self)



        self.window.chat_input.returnPressed.connect(self.addMsg)
        self.window.msg_left.setAlignment(QtCore.Qt.AlignLeft)
        self.window.msg_right.setAlignment(QtCore.Qt.AlignRight)


        self.current_contact = None
        self.current_contact_uid = None
        self.layout_dic = {0: self.window.msg_left, 1: self.window.msg_right}



    def addEmoji(self, emoji):
        self.window.chat_input.setText("{0}{1}".format(self.window.chat_input.text(), emoji))


    def reply(self, uid):
        username = self.network.getUbu(uid)
        if uid == self.uid or not username:
            return
        self.window.chat_input.setText("@{0} {1}".format(username, self.window.chat_input.text()))

    def getDate(self, d1):
        d1, d2 = datetime.now(), datetime.fromtimestamp(d1)
        days = d1.day - d2.day

        if days == 0:
            d = "today"
        elif days == -1:
            d = "yesterday"
        else:
            d = "{0} days ago".format(days)
        return "{0} at {1}".format(d, d2.strftime("%H:%M"))


    def addMsg(self, msg=None, username=None, uid=None, db=True, from_self=False):
        username = username if username else self.username
        uid = uid if uid else self.uid
        error = False
        if not msg:
            msg = self.window.chat_input.text()
            self.window.chat_input.setText("")
            from_self = True

        if not msg.strip():
            return
        if db:
            if len(self.network.data[self.current_contact_uid]["msgs"]) >= MAX_MSG:
                self.network.data[self.current_contact_uid]["msgs"].clear()
            data = {'author': self.username, 'author_id': self.uid, 'text': msg, 'id': randUid(12), 'date': timestamp()}
            self.network.data[self.current_contact_uid]["msgs"].append(data)

        if from_self:
            self.loop.run_until_complete(self.apic.sendMessage(
                msg, self.uid, self.username, self.current_contact_uid
            ))
            if not self.apic.latest:
                error = True

        self.createEmpty(self.layout_dic[not from_self])
        self.createMsg(msg, username, uid, int(timestamp()), self.layout_dic[from_self], error, from_self=from_self)

    def createMsg(
        self,
        text,
        author,
        author_id,
        date,
        msg_layout,
        post = False,
        error=False,
        from_self=False,
        auto_empty = False
    ):


        ## text frame ##
        textframe = QtWidgets.QFrame(self.window.scrollAreaWidgetContents_3)
        _len = len(text)
        _len = _len*_len
        _height = 100

        if _len < 100:
            _len = 150
        if _len > 300:
            _len = 300
            _height += 50
        textframe.setMaximumSize(QtCore.QSize(_len, _height))

        ##009c99
        textframe.setStyleSheet("background-color: {0}".format('#f0eee9;' if not from_self else '#48c3d9;'))
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
        button.setStyleSheet("border: 0px solid {0}".format('#f0eee9;' if not from_self else '#48c3d9;'))
        button.setObjectName("toolButton")
        layout.addWidget(button)

        ## text browser ##
        browser = QtWidgets.QTextBrowser(textframe)
        browser.setMaximumSize(300, 150)
        browser.setObjectName("textBrowser")
        layout.addWidget(browser)



        ## set text ##

        browser.setText("<p>{0}</p>".format(text)) # use h tag
        b_text = "{0} {1}".format('' if from_self else "{0} - ".format(author), self.getDate(date))
        button.setText(b_text)

        ## add to layout ##
        if auto_empty:
            self.createEmpty(auto_empty, _len, _height)
        msg_layout.addWidget(textframe)
        self.window.scrollArea_3.verticalScrollBar().setValue(self.window.scrollArea_3.verticalScrollBar().maximum())


    def emojize(self):
        self.window.chat_input.setText(emojis.encode(self.window.chat_input.text()))

    def createEmpty(self, layout, w=310, h=160):
        label = QtWidgets.QLabel(self.window.scrollAreaWidgetContents_3)
        label.setMinimumSize(w, h)
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
        self.window.chat_input.setPlaceholderText("Send a message to {0}".format(name))
        self.current_contact = name
        self.current_contact_uid = uid

        self.deleteCurrent(self.window.msg_left)
        self.deleteCurrent(self.window.msg_right)

        for msg in self.network.data[uid]["msgs"]:
            self.network.label_added.append(msg["id"])
            if msg["author_id"] == self.uid:
                self.createMsg(
                    msg["text"],
                    "{0} ({1})".format(self.username, 'you'),
                    msg["author_id"],
                    msg["date"],
                    self.window.msg_right,
                    from_self=True,
                    auto_empty=self.window.msg_left
                )


            else:
                self.createMsg(
                        msg["text"],
                        msg["author"],
                        msg["author_id"],
                        msg["date"],
                        self.window.msg_left,
                        auto_empty=self.window.msg_right
                    )


    def getContactButtons(self, window, widget, contacts):
        for contact in contacts:
            b = QtWidgets.QPushButton(window)
            widget.addWidget(b)
            b.setText(contact.name)
            b.clicked.connect(partial(self.clickedContact, (contact.uid, contact.name)))
            self.network.button_values[contact.uid] = b
        widget.addItem(QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
