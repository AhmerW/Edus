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

class Message(QtWidgets.QFrame):
    def __init__(self, width, height, text, author, uid, date, layout, from_self=False, *a, **kw):
        super().__init__()
        self.text = text
        self.setMaximumSize(QtCore.QSize(width, height))
        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.setFrameShadow(QtWidgets.QFrame.Raised)
        self.stylesheet = "background-color: {0}".format('#f0eee9;' if not from_self else '#48c3d9;')

        ## message layout ##
        self.layout = QtWidgets.QVBoxLayout(self)

        ## author and date buton ##
        self.button = QtWidgets.QToolButton(self)
        self.button.setStyleSheet("border: 0px;")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button.sizePolicy().hasHeightForWidth())


        ## text browser ##
        self.browser = QtWidgets.QTextBrowser(self)
        self.browser.setText("<p>{0}</p>".format(self.text))
        self.browser.setStyleSheet("border: 0px;")
        self.browser.setMaximumSize(300, 800) # 300, 150



    def create(self):
        self.setStyleSheet(self.stylesheet)
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.browser)


class LineFrame(QtWidgets.QFrame):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        ## frame ##
        self.setMaximumHeight(50)
        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.setFrameShadow(QtWidgets.QFrame.Raised)
        self.layout = QtWidgets.QHBoxLayout(self)

        ## lines ##
        self.line1 = self.createLine()
        self.line2 = self.createLine()

        ## text ##
        self.label = QtWidgets.QLabel(self)
        self.label.setMaximumSize(QtCore.QSize(50, 16777215))

    def createLine(self):
        line = QtWidgets.QFrame(self)
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)

    def create(self):
        self.layout.addWidget(self.line1)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.line2)

class Chat(object):
    def __init__(self, window, network, apic, loop, login):
        self.window = window
        self.network = network
        self.apic = apic
        self.loop = loop
        self.login = login
        self.dialog_emoji = EmojiDialog(self)

        self.window.chat_input.returnPressed.connect(self.addMsgSelf)

        ## chat data ##
        self.contacts = []
        self.frames = {}
        self.latest_by_self = False
        self.latest_by_self_time = None
        self.current_contact = None
        self.current_contact_uid = None
        self.current_contact_channel = None
        self.layout_dic = {0: QtCore.Qt.AlignLeft, 1: QtCore.Qt.AlignRight}



    def addEmoji(self, emoji):
        self.window.chat_input.setText("{0}{1}".format(self.window.chat_input.text(), emoji))

    def clear(self, text):
        if '<' in text and '>' in text:
            return "<{0}>".format(text)
        return text

    def getDate(self, d1):
        d1, d2 = datetime.now(), datetime.fromtimestamp(d1)
        days = d1.day - d2.day

        if days == 0:
            d = "today at"
        elif days == -1:
            d = "yesterday at"
        else:
            return "{0}/{1}".format(d2.month, d2.day)
        return "{0} {1}".format(d, d2.strftime("%H:%M"))

    def addMsgSelf(self):
        frame = self.frames.get(self.current_contact_uid)
        if not frame:
            return
        text = self.window.chat_input.text().strip()
        if not text:
            return
        #for emoji in emojis.get(text):
            #text = text.replace(emoji, '<h1>{0}</h1>'.format(emoji))
        self.createMsg(
            text=text,
            author=self.login.username,
            uid=self.login.uid,
            date=int(timestamp()),
            layout=frame["layout"],
            from_self=True,
            side=self.layout_dic[1]
        )
        self.window.chat_input.setText("")

        self.latest_by_self = True
        self.latest_by_self_time = timestamp()
        self.loop.run_until_complete(self.apic.sendMessage(
            text,
            self.login.uid,
            self.login.username,
            self.current_contact,
            self.current_contact_uid,
            self.login.token
        ))

    def addMsg(self, msg, username, uid):
        if not msg.strip():
            return

        frame = self.frames.get(uid)
        if not frame:
            return

        self.createMsg(msg, username, frame["layout"],side=self.layout_dic[False])
        self.latest_by_self = False

    def createMsg(self, *args, **kwargs):
        text = self.clear(kwargs.get('text'))
        from_self = kwargs.get('from_self')
        pl = 120 if from_self else 200
        _width = len(text)+pl
        _height = 100
        if _width > 300:
            _width = 300
            _height += 50

        message = Message(_width, _height, *args, **kwargs)
        if not self.latest_by_self:
            message.stylesheet +=  " border: 1px solid aqua;"
        date = self.getDate(kwargs.get('date'))
        message.button.setText(date if from_self else "{0} - {1}".format(kwargs.get('author'), date))

        message.create()

        kwargs.get('layout').addWidget(message, 0, alignment=kwargs.get('side'))

    def emojize(self):
        self.window.chat_input.setText(emojis.encode(self.window.chat_input.text()))


    def deleteCurrent(self, layout):
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().setParent(None)


    def getLayouts(self, uid):
        if uid in self.frames:
            return self.frames[uid]
        return self.window.scrollchat_frame, self.window.msg_left, self.window.msg_right

    def loadFrame(self, frame, layout):
        if not self.current_contact_uid:
            return

        self.gridLayout_16.addWidget(self.frame_text, 0, 0, 1, 2)

    def createFrame(self):
        frame = QtWidgets.QFrame(self.window.scrollAreaWidgetContents_3)

        frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        frame.setFrameShadow(QtWidgets.QFrame.Raised)
        layout = QtWidgets.QVBoxLayout(frame)



        left = QtWidgets.QVBoxLayout()
        left.setSpacing(0)
        left.setAlignment(QtCore.Qt.AlignLeft)


        return frame, layout

    def clickedContact(self, contact):
        uid, name = contact.uid, contact.name
        if self.current_contact == name:
            return
        self.window.chat_input.setPlaceholderText("Send a message to {0}".format(name))
        self.current_contact = name
        self.current_contact_uid = uid
        frame = self.frames.get(uid)
        if frame:
            frame, layout = frame.get("frame"), frame.get("layout")
        else:
            frame, layout = self.createFrame()
            self.frames[uid] = {"frame": frame, "layout": layout}
        self.deleteCurrent(self.window.gridLayout_16)
        return self.window.gridLayout_16.addWidget(frame, 0, 0, 1, 2)



    def createContactButtons(self, window, widget, contacts):

        first = contacts[0] if len(contacts) > 1 else None
        for contact in contacts:
            b = QtWidgets.QPushButton(window)
            widget.addWidget(b)
            b.setText(contact.name)
            b.clicked.connect(partial(self.clickedContact, contact))
            self.network.button_values[contact.uid] = b
        self.contact_spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        widget.addItem(self.contact_spacer)
        if first:
            self.clickedContact(first)
