
import os
import json
from lib.security.gen import randUid

class User(object):
    """Represents an user in Edus."""
    def __init__(self, uid, name):
        self.uid : int = uid
        self.name : str = name
        self.msgs : list = []
        self.admin : bool = False
    def __str__(self):
        return self.name

class Student(User):
    pass

class Teacher(User):
    pass

class Contact(object):
    def __init__(self, *args, **kwargs):
        for detail, value in kwargs.items():
            setattr(self, detail, value)


class Classroom(object):
    def __init__(self, name):
        self.name = name
        self.cid = randUid( )# class id

class Network(object):
    def __init__(self, window):
        self.window = window
        self.label_added = []
        self.contacts = ["hi"]
        self.classrooms = [Classroom("Home")]
        self.ubu = {}

        self.button_values = {}


    def createContact(self, contact):
        pass

    def addContacts(self, contacts):
        pass

    def getUbu(self, uid):
        """username by uid (ubu)"""
        return self.ubu.get(uid)

    def exitSave(self):
        for contact in self.contacts:
            pass


    def getPath(self, path, *args):
        return os.path.join(os.path.abspath(path), *args)
