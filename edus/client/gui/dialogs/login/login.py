from PyQt5 import QtWidgets
from PyQt5 import QtCore, uic, QtGui
import os

class LoginDialog(QtWidgets.QDialog):
    def __init__(self):
        super(LoginDialog, self).__init__()
        uic.loadUi(os.path.join(os.path.abspath('gui'), 'dialogs', 'login', 'login.ui'), self)
