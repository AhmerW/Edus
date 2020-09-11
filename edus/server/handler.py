import socket

class EventHandler():
    def __init__(self, data):
        self.data = data

    async def handle(self, sock):
        uid = sock.recv(1080).decode('utf-8')
        if not self.data.get(uid):
            ## return false
            ## and possible in client side say
            ## 'could not verify authentity', etc..
            return
        self.data[uid]['server'] = sock

    async def send(self, sock):
        pass
