
import os
import json
from lib.security.gen import randUid

class Person(object):
    """Represents a person in Edus."""
    def __init__(self, uid, name):
        self.uid : int = uid
        self.name : str = name
        self.msgs : list = []
        self.admin : bool = bool(self.uid)
    def __str__(self):
        return self.name

class Student(Person):
    pass

class Teacher(Person):
    pass

class Classroom(object):
    def __init__(self, name):
        self.name = name
        self.cid = randUid( )# class id

class Network(object):
    def __init__(self, window):
        self.window = window
        self.label_added = []
        self.contacts = []
        self.classrooms = [Classroom("Home")]
        self.ubu = {}
        self.data = self.getData('contacts.json')
        for uid, contact in self.data.items():
            self.ubu[uid] = contact["name"]
            self.contacts.append(Person(uid, contact['name']))
        self.current_contact = self.contacts[0].uid

        self.button_values = {}



    def getUbu(self, uid):
        """username by uid (ubu)"""
        return self.ubu.get(uid)

    def exitSave(self):
        for contact in self.contacts:
            pass

    def getPath(self, path, *args):
        return os.path.join(os.path.abspath(path), *args)

    def getData(self, path):
        with open(self.getPath('cache', path), "r") as f:
            try:
                return json.load(f)
            except ValueError:
                return {}


    def createConctact(self, name):
        uid = randUid()
        contact = Person(uid, name)
        with open(self.getPath('cache', 'contacts.json'), "w+") as f:
            try:
                data = json.load(f)
            except:
                data = {}
            data[uid] = {"name": name, "msgs": []}
            json.dump(data, f, indent=2)


        return contact
