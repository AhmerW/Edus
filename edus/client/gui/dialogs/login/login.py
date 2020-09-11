from PyQt5 import QtWidgets
from PyQt5 import QtCore, uic, QtGui
from hashlib import sha256
import asyncio
import os
from lib.web.netevent import NetworkEvents
from gui.dialogs.login.register import RegisterDialog

loop = asyncio.get_event_loop()

class LoginDialog(QtWidgets.QDialog):
    def __init__(self, event):
        super(LoginDialog, self).__init__()
        ##objects##
        self.event = event
        self.register_dialog = RegisterDialog(self.event.apic)
        uic.loadUi(os.path.join(os.path.abspath('gui'), 'dialogs', 'login', 'login.ui'), self)

        ##data##
        self.logged_in = False

        ##register buton##
        self.login_button.clicked.connect(self.login)
        self.register_button.clicked.connect(self.startRegister)

    def login(self):
        email, password = self.email.text(), self.password.text()
        if not email.strip() or not password.strip():
            return self.status.setText("Some values are missing!")

        r = loop.run_until_complete(self.event.apic.basic(
            {"email": email, "password": sha256(password.encode()).hexdigest()},
            'login'
        ))
        if r.get('status'):
            status = "Login successfull!"
            self.event.netevent = NetworkEvents('localhost', 8989, r.get('uid'))
            self.event.registerEvents()
        else:
            status = "Login failed!"
        self.status.setText(status)

    def startRegister(self):
        self.register_dialog.show()
