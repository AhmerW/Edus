import socket

class EventHandler():
    def __init__(self, data):
        self.data = data

    async def handle(self, sock):
        uid = sock.recv(1080).decode('utf-8')
        uid = int(uid) if uid.isdigit() else None
        if not self.data.get(uid):
            ## return false
            ## and possible in client side say
            ## 'could not verify authentity', etc..
            return
        self.data[uid]['client'] = sock

    async def send(self, sock):
        pass
