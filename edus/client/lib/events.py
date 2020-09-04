from PyQt5 import QtWidgets, QtCore
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
        self.classroom_buttons = {}
        self.previous = None

    def loadClassrooms(self, func=None, search=False):
        if search:
            search = self.window.input_classroom_search.text().lower().strip()
            if not search:
                search = False
            else:
                classrooms = [classroom for classroom in self.network.classrooms if search in classroom.name.lower()]
        if not search:
            classrooms = self.network.classrooms
            title_text = "Classrooms ({0})"
        else:
            title_text = "Found {0} classrooms matching your search."

        self.window.groupbox_classroom.setTitle(title_text.format(len(classrooms)))
        #i = 0
        for i, classroom in enumerate(self.network.classrooms):
            if search:
                if not classroom in classrooms:
                    print("not")
                    button = self.classroom_buttons.get(classroom)
                    if button:
                        button.deleteLater()
                        del self.classroom_buttons[classroom]
                        #button.setStyleSheet("background-color: green;")
                        continue
            button = QtWidgets.QPushButton(self.window.scrollAreaWidgetContents_2)

            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(button.sizePolicy().hasHeightForWidth())

            button.setSizePolicy(sizePolicy)
            button.setMinimumSize(QtCore.QSize(100, 100))
            button.setMaximumSize(QtCore.QSize(600, 16777215))
            button.setText(classroom.name)
            button.setStyleSheet("")

            self.window.gridLayout_17.addWidget(button, i, 0, 1, 1)
            self.classroom_buttons[classroom] = button
            if func:
                button.clicked.connect(partial(
                    func,
                    'classroom_button',
                    '<h1>{0}</h1>'.format(classroom.name),
                    classroom.cid
                ))
            #i += 1
        self.window.gridLayout_17.update()


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