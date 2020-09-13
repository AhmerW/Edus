from PyQt5 import QtWidgets
from PyQt5 import QtCore, uic, QtGui

class FriendDialog(QtWidgets.QDialog):
    def __init__(self, api):
        super(FriendDialog, self).__init__()
        self.api = api
        uic.loadUi(os.path.join(os.path.abspath('gui'), 'dialogs', 'friend', 'friend.ui'), self)

    
