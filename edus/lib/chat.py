from PyQt5.QtWidgets import QPushButton, QLabel
from functools import partial
import typing

class Chat(object):
    def __init__(self, window, network):
        self.window = window
        self.network = network

    def clickedContact(self, contact : typing.Tuple[str, str]):
        uid, name = contact
        msgs = self.network.data[uid]["msgs"]
        for msg in msgs:
            if msg["id"] in self.network.label_added:
                continue
            self.network.label_added.append(msg["id"])
            label = QLabel(self.window.scrollAreaWidgetContents_2)
            label.setText(msg["text"])
            self.window.verticalLayout_10.addWidget(label)

    def getContactButtons(self, window, widget, contacts):
        for contact in contacts:
            b = QPushButton(window)
            widget.addWidget(b)
            b.setText(contact.name)
            b.clicked.connect(partial(self.clickedContact, (contact.uid, contact.name)))
            self.network.button_values[contact.uid] = b
