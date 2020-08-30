from PyQt5.QtWidgets import QPushButton, QLabel
from functools import partial
import typing
from lib.caching import CustomCache
from lib.network import Network
from lib.chat import Chat

class Events(object):
    def __init__(self, window):
        self.window = window
        self.network = Network(self.window)
        self.chat = Chat(self.window, self.network)
        self.previous = None



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
