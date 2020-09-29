import os
import asyncio
from PyQt5 import QtWidgets
from PyQt5 import QtCore, uic, QtGui

loop = asyncio.get_event_loop()

class FriendDialog(QtWidgets.QDialog):
    def __init__(self, api, login):
        super(FriendDialog, self).__init__()
        self.api = api
        self.login = login
        uic.loadUi(os.path.join(os.path.abspath('gui'), 'dialogs', 'friend', 'friend.ui'), self)

    def send(self):
        res = loop.run_until_complete(self.api.basic(
            {'from': self.uid,'target': self.entry.get(), 'uid': self.login.uid, 'token': self.login.token},
            'friend/add/'
        ))

        print("friend add results", res)
