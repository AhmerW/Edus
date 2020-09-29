from PyQt5 import QtWidgets, QtGui, QtCore, uic
from functools import partial
import random
import asyncio
import json
import sys
import os
from lib.events import Events
from lib.customs import ButtonDropdown
from  lib.network import Contact

class Startup(QtWidgets.QDialog):
    def __init__(self, window, *args, **kwargs):
        super(Startup, self).__init__(*args, **kwargs)
        self.window = window
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowTitleHint | QtCore.Qt.CustomizeWindowHint)
        uic.loadUi(os.path.join(os.path.abspath('gui'), 'dialogs', 'startup', 'startup.ui'), self)
        self.logged_in = False
        self.success = False

    def proceed(self):
        loop = asyncio.get_event_loop()
        res = loop.run_until_complete(self.window.events.apic.gather(
            self.window.events.login.token,
            self.window.events.login.uid
        ))
        print(res)
        self.window.events.login.username = res.get('username')
        self.window.events.login.tag = res.get('tag')
        friends = res.get('friends')
        if not friends:
            try:
                friends = json.loads(friends)
            except Exception: friends = {}
        else:
            friends = {}
        friends["john"] = {"uid": 123}
        for friend, values in friends.items():
            self.window.events.chat.contacts.append(Contact(
                name=friend,
                uid=values.get("uid")
            ))
            self.window.events.chat.createContactButtons(
                self.window.contact_frame,
                self.window.verticalLayout_10,
                self.window.events.chat.contacts
            )
        self.close()

    def check(self):
        if self.logged_in:
            return self.close()
        self.window.events.login.exec_()
        self.success = self.window.events.login.logged_in
        if not self.success:
            return self.close()

        self.proceed()

    def start(self):
        QtCore.QTimer.singleShot(2000, self.check)
        self.show()
        self.exec_()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi(os.path.join(os.path.abspath('gui'), 'edus.ui'), self)
        self.events = Events(self)
        self.startup = Startup(self)



        ## tabs ##
        self.button_tabs = {
            self.tab_welcome: (None, "Welcome"),
            self.button_chat: (self.tab_chat, "Chat"),
            self.button_classrooms: (self.tab_classrooms, "Classrooms"),
            self.button_teachers: (self.tab_teachers, "Teachers"),
            self.button_activity: (self.tab_activity, "Activity"),
            'classroom_button': (self.tab_classroom_chat, "Classroom Chat")
        }
        self.tab_welcome.setStyleSheet("background-color: white;")
        self.cbut = None
        ## call functions ##
        self.classroom_search_button.clicked.connect(partial(
            self.events.loadClassrooms,
            self.onClick,
            True
        ))
        self._b_ss = "border-radius: 20px; margin 5px; border-style: solid; border-width: 2px;"

        self.startWelcome()
        self.bindButtons()
        self.startup.close()

    def closeEvent(self, event):
        if hasattr(self.events.netevent, 'sock'):
            print("closed")
            self.events.netevent.sock.close()
        event.accept()

    def startWelcome(self):
        for tab in list(self.button_tabs.keys()):
            if isinstance(self.button_tabs[tab][0], QtWidgets.QWidget):
                self.button_tabs[tab][0].setStyleSheet("")
            self.tabWidget.removeTab(1)
        for button in self.button_tabs:
            if isinstance(button, QtWidgets.QToolButton):
                button.setStyleSheet(self._b_ss)


    def bindButtons(self):
        for item, obj in self.__dict__.items():
            if isinstance(obj, QtWidgets.QPushButton) or isinstance(obj, QtWidgets.QToolButton):
                obj.clicked.connect(
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
                        self.cbut.setStyleSheet(self._b_ss)
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
        actions = {
            self.events.login.username: 0,
            'login': 'button_login',
            'profile': 0,
            'Settings': 0
        }
        frame = QtWidgets.QFrame(self)
        action_objects = []
        self.dropdown_name_menu = QtWidgets.QMenu(frame)
        self.dropdown_name = ButtonDropdown()
        self.dropdown_name.setIcon(QtGui.QIcon(os.path.join('gui', 'assets', 'default.png')))
        self.dropdown_name.setText("Name")

        for name, arg in actions.items():
            action = QtWidgets.QAction(name, self)
            action.triggered.connect(partial(self.onClick, action, name if not bool(arg) else arg))
            self.dropdown_name_menu.addAction(action)
            action_objects.append(action)

        self.dropdown_name.setMinimumSize(150, 50)
        self.dropdown_name.setMenu(self.dropdown_name_menu)
        self.dropdown_name.setDefaultAction(action_objects[0])
        print(dir(self.dropdown_name))
        self.horizontalLayout_2.addWidget(self.dropdown_name)

    def mousePressEvent(self, event):
        if event.buttons() == QtCore.Qt.RightButton:
            print("right")

    def start(self, app):
        self.startup.start()
        if not self.startup.success:
            print("failed")
            return
        self.createOthers()
        self.show()
        sys.exit(app.exec_())

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.start(app)
