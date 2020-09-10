import socket
import asyncio
import threading
from time import sleep
from contextlib import closing
from handler import EventHandler



class Auth(object):
    def __init__(self):
        self.db = {}

    async def verifyLogin(self, username, password):
        return self.db.get(username) == password

    async def register(self, username, password):
        if self.db.get(username):
            return False
        self.db[username] = password
        return True

class Gateway():
    def __init__(self, host = 'localhost', port = 8991):
        self.host, self.port = host, port
        self.loop = asyncio.get_event_loop()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.auth = Auth()

        self.tasks = []
        self.data = {}
        self.event_servers = {}
        self.listen_servers = {}
        self.started = False

    async def checkSocket(self, socket, host, port):
        try:
            self.sock.bind((self.host, self.port))
            return True
        except:
            return False

    async def spawnEventServer(self, amount=1):
        for _ in range(amount):
            self.event_servers[EventHandler(self.data)] = 0

    async def getServer(self, servers):
        return min(servers, key = lambda i : servers[i])

    async def handle(self, c):
        server = await self.getServer(self.event_servers)
        self.event_servers[server] += 1
        tasks = [await self.loop.create_task(server.handle(c))]
        if tasks:
            await asyncio.wait(*tasks)


    def actual(self):
        print("server listening")
        while self.started:
            c, _ = self.sock.accept()
            self.loop.run_until_complete(self.handle(c))

    async def run(self):

        while not self.started:
            if await self.checkSocket(self.sock, self.host, self.port):
                self.started = True
                break
            sleep(2)
            self.port += 1
        await self.spawnEventServer(2)
        self.sock.listen()
        threading.Thread(target=self.actual).start()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    gateway = Gateway(loop)

    loop.create_task(gateway.start())
