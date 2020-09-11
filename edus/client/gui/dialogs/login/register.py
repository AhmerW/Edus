from PyQt5 import QtWidgets
from PyQt5 import QtCore, uic, QtGui
from hashlib import sha256
import asyncio
import os

loop = asyncio.get_event_loop()

class RegisterDialog(QtWidgets.QDialog):
    def __init__(self, api):
        super(RegisterDialog, self).__init__()
        self.api  = api
        uic.loadUi(os.path.join(os.path.abspath('gui'), 'dialogs', 'login', 'register.ui'), self)
        self.register_button.clicked.connect(self.register)

    def register(self):
        pass1, pass2 = self.password.text(), self.password_again.text()
        username = self.username.text()
        email = self.email.text()

        if not any(str(x).strip() for x in [pass1, pass2, username, email]):
            return self.status.setText("Some values are missing!")

        pass1, pass2 = sha256(pass1.encode()).hexdigest(), sha256(pass2.encode()).hexdigest()
        if not pass1 == pass2:
            self.status.setText("Password does not match!")
            return

        r = loop.run_until_complete(self.api.basic(
            {"email": email, "password": pass1, "username": username},
            'register'
        ))
        if r.get('uid'):
            status = "Successfully registered. Welcome {0}".format(username)
        else:
            status = "Could not register. Try again"
        self.status.setText(status)
