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
        dif = d1 - d2
        if dif.days == 0:
            d = "today"
        elif dif.days == -1:
            d = "yesterday"
        else:
            d = "{0} days ago".format(dif.days)
        hours = int(dif.total_seconds()/3600)
        _type = 'hours'
        if hours == 0:
            _type = 'minutes'
            hours = int(hours*60)
        text = "{0} {1}{2} ago".format(hours, _type, 's' if hours == 1 else '')
        return "{0} at {1}".format(text, "{0}:{1}".format(d2.hour, d2.minute))


    def addMsg(self, msg=None, username=None, uid=None, db=True, from_self=True):
        username = username if username else self.username
        uid = uid if uid else self.uid
        error = False
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

        if from_self:
            self.loop.run_until_complete(self.apic.sendMessage(
                msg, self.uid, self.username, self.current_contact_uid
            ))
            if not self.apic.latest:
                error = True

        self.createEmpty(self.layout_dic[not from_self])
        self.createMsg(msg, username, uid, int(timestamp()), self.layout_dic[from_self], error)

    def createMsg(self, text, author, author_id, date, msg_layout, error=False):


        ## text frame ##
        textframe = QtWidgets.QFrame(self.window.scrollAreaWidgetContents_3)
        textframe.setMaximumSize(QtCore.QSize(300, 150))
        textframe.setStyleSheet("background-color: {0}".format('#009c99;' if not error else '#49676b;'))
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

        browser.setText(text) # use h tag
        b_text = "Not sent" if error else "By {0} - {1}".format(author, self.getDate(date))
        button.setText(b_text)
        reply_button.setText("reply" if not error else "retry")
        if error:
            reply_button.clicked.connect(partial(
                self.addMsg,
                text,
                author,
                author_id,
                False,
                True
            ))
        else:
            reply_button.clicked.connect(partial(self.reply, author_id))

        ## add to layout ##
        layout.addWidget(reply_button)

        msg_layout.addWidget(label)
        msg_layout.addWidget(textframe)
        self.window.scrollArea_3.verticalScrollBar().setValue(self.window.scrollArea_3.verticalScrollBar().maximum())


    def emojize(self):
        self.window.chat_input.setText(emojis.encode(self.window.chat_input.text()))

    def createEmpty(self, layout):
        label = QtWidgets.QLabel(self.window.scrollAreaWidgetContents_3)
        label.setMinimumSize(330, 180)
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
        widget.addItem(QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
