from PyQt5 import QtWidgets
from PyQt5 import QtCore, uic


class ButtonDropdown(QtWidgets.QToolButton):
    def __init__(self, parent=None):
        super(ButtonDropdown, self).__init__(parent)
        self.setPopupMode(self.MenuButtonPopup)
        self.triggered.connect(self.setDefaultAction)
