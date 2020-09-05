import socket
import threading
from time import sleep





class NetworkEvents(threading.Thread):
    def __init__(self, ip, port):
        super(NetworkEvents, self).__init__()
        self.ip, self.port = ip, port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False

        self.events = {
            "on_friend_request": None,
            "on_message": None
        }

    def registerEvent(self, event):
        def inner(func):
            def wrap(*args, **kwargs):
                if self.events.get(event):
                    self.events[event] = func
                return func(*args, **kwargs)
            return wrap

        return inner

    def connect(self):
        try:
            self.sock.connect((self.ip, self.port))
            self.connected = True
            return True
        except Exception as e:
            print("Connection error ", e)
            return False

    def run(self):
        while not self.connected:
            if not self.connect():
                sleep(2)
        print("connected")
        while self.connected:
            event = self.sock.recv(2080).decode() # event:data
            if not ':' in event:
                continue
            event, data = event.split(':')
            func = events.get(event)
            if callable(func):
                func(data)
