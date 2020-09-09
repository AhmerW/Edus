from PyQt5 import QtWidgets
from PyQt5 import QtCore, uic, QtGui
import asyncio
import os

loop = asyncio.get_event_loop()

class LoginDialog(QtWidgets.QDialog):
    def __init__(self, api):
        super(LoginDialog, self).__init__()
        self.api  = api
        uic.loadUi(os.path.join(os.path.abspath('gui'), 'dialogs', 'login', 'login.ui'), self)
        self.login_button.clicked.connect(self.login)
    def login(self):
        r = loop.run_until_complete(self.api.login(
            self.email.text(),
            self.password.text()
        ))
        print(self.api.latest_login, r)
