from PyQt5 import QtWidgets, QtCore
from functools import partial
import asyncio
import typing
from gui.dialogs.friend.friend import FriendDialog
from gui.dialogs.login.login import LoginDialog
from lib.web.netevent import NetworkEvents
from lib.caching import CustomCache
from lib.network import Network
from lib.web.apic import Calls
from lib.chat import Chat


loop = asyncio.get_event_loop()


class ProcessEvent(object):
    def __init__(self):
        pass

    def on_message(self, msg):
        print(msg)

    def on_friend_request(self, data):
        print(data)

class Events(object):
    def __init__(self, window):
        self.window = window
        ## objects ##
        self.netevent = None
        self.apic = Calls()
        self.friend = FriendDialog(self.apic)
        self.processor = ProcessEvent()
        self.network = Network(self.window)
        self.login = LoginDialog(self)
        self.chat = Chat(self.window, self.network, self.apic, loop, self.login)

        self.classroom_buttons = {}
        self.previous = None
        self.commands = {
            'button_login': self.login.show,
            'button_new': self.friend.show,
            'emoji_dialog': self.chat.dialog_emoji.start,
            'chat_send': self.chat.addMsg,
            'emojize': self.chat.emojize
        }

    def registerEvents(self):
        for event in dir(self.processor):
            func = getattr(self.processor, event)
            _ev = self.netevent.events.get(event)
            if callable(func) and _ev:
                self.netevent.events[_ev] = func
        if hasattr(self.netevent, 'start'):
            self.netevent.start()

    def loadClassrooms(self, func=None, search=False):
        if search:
            search = self.window.input_classroom_search.text().lower().strip()
            if search:
                classrooms = [classroom for classroom in self.network.classrooms if search in classroom.name.lower()]
        if not bool(search):
            classrooms = self.network.classrooms
            title_text = "Classrooms ({0})"
        else:
            title_text = "Found {0} classrooms matching your search."

        self.window.groupbox_classroom.setTitle(title_text.format(len(classrooms)))
        #i = 0
        for i, classroom in enumerate(self.network.classrooms):
            if search:
                if not classroom in classrooms:
                    button = self.classroom_buttons.get(classroom)
                    if button:
                        button.deleteLater()
                        del self.classroom_buttons[classroom]
                        #button.setStyleSheet("background-color: green;")
                        continue
            button = QtWidgets.QPushButton(self.window.scrollAreaWidgetContents_2)

            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(button.sizePolicy().hasHeightForWidth())

            button.setSizePolicy(sizePolicy)
            button.setMinimumSize(QtCore.QSize(100, 100))
            button.setMaximumSize(QtCore.QSize(600, 16777215))
            button.setText(classroom.name)

            self.window.gridLayout_17.addWidget(button, i, 0, 1, 1)
            self.classroom_buttons[classroom] = button
            if func:
                button.clicked.connect(partial(
                    func,
                    'classroom_button',
                    '<h1>{0}</h1>'.format(classroom.name),
                    classroom.cid
                ))
            #i += 1
        #self.window.gridLayout_17.update()


    def loadTab(self, tab, name):

        if name == "chat":
            if self.previous == self.network.contacts:
                self.network.button_values[self.network.current_contact].click()
                return tab
            value = self.chat.getContactButtons(
                self.window.scrollAreaWidgetContents,
                self.window.verticalLayout_5,
                self.network.contacts
            )
            self.previous = self.network.contacts
            self.network.button_values[self.network.current_contact].click()
        return tab

    def processOther(self, name, other=None):
        command = self.commands.get(name)
        if callable(command):
            command()
