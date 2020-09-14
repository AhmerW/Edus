from PyQt5 import QtWidgets
from PyQt5 import QtCore, uic
from functools import partial
import sys
import os
from lib.events import Events
from lib.customs import ButtonDropdown


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi(os.path.join(os.path.abspath('gui'), 'edus.ui'), self)
        self.events = Events(self)


        ## tabs ##
        self.button_tabs = {
            self.tab_welcome: (None, "Welcome"),
            self.button_chat: (self.tab_chat, "Chat"),
            self.button_classrooms: (self.tab_classrooms, "Classrooms"),
            self.button_teachers: (self.tab_teachers, "Teachers"),
            self.button_activity: (self.tab_activity, "Activity"),
            'classroom_button': (self.tab_classroom_chat, "Classroom Chat")
        }
        self.cbut = None
        ## call functions ##
        self.classroom_search_button.clicked.connect(partial(
            self.events.loadClassrooms,
            self.onClick,
            True
        ))

        self.startWelcome()
        self.createOthers()
        self.bindButtons()

    def closeEvent(self, event):
        if hasattr(self.events.netevent, 'sock'):
            self.events.netevent.sock.close()
        event.accept()

    def startWelcome(self):
        for _ in range(len(self.button_tabs)-1):
            self.tabWidget.removeTab(1)


    def bindButtons(self):
        for item in self.__dict__:
            obj = self.__dict__[item]
            if isinstance(obj, QtWidgets.QPushButton) or isinstance(obj, QtWidgets.QToolButton):
                self.__dict__[item].clicked.connect(
                    partial(
                        self.onClick,
                        obj,
                        item
                    )
                )

    def onClick(self, obj, name, special=None):
        if self.button_tabs.get(obj):
            try:
                tab, text = self.button_tabs[obj]
                if not tab:
                    return
                if isinstance(obj, QtWidgets.QToolButton):
                    if self.cbut:
                        self.cbut.setStyleSheet("")
                    self.cbut = obj
                    obj.setStyleSheet("border-left: 5px solid aqua;")
                tab = self.events.loadTab(tab, text.lower())
                if tab == self.tab_classrooms:
                    self.events.loadClassrooms(self.onClick)
                if obj == 'classroom_button':
                    self.classroom_name.setText(name)
                self.tabWidget.removeTab(0)
                self.tabWidget.insertTab(0, tab, text)
            except AttributeError:
                return
        else:
            self.events.processOther(name, special)

    def createOthers(self):
        ## dropdown button for name, found in top right ##
        actions = [
            'Settings'
        ]
        self.dropdown_name_menu = QtWidgets.QMenu(self)
        self.dropdown_name = ButtonDropdown()
        self.dropdown_name.setText("Name")

        self.dropdown_name.setMinimumSize(150, 50)
        self.horizontalLayout_2.addWidget(self.dropdown_name)

    def mousePressEvent(self, event):
        if event.buttons() == QtCore.Qt.RightButton:
            print("right")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
