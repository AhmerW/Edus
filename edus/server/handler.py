import socket

class EventHandler():
    def __init__(self, data):
        self.data = data

    async def handle(self, sock):
        uid = self.sock.recv(2080).decode('utf-8')
        if len(uid) != 20 or uid in self.data:
            sock.close()
