import socket

class EventHandler():
    def __init__(self, data):
        self.data = data

    async def handle(self, sock):
        uid = sock.recv(1080).decode('utf-8')
        if not self.data.get(uid):
            return
        self.data[uid]['server'] = sock

    async def send(self, sock):
        pass
