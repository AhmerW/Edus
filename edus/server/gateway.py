import socket
import asyncio
import threading
from time import sleep
from contextlib import closing
from handler import EventHandler

class Gateway(object):
    def __init__(self, loop, host = 'localhost', port = 8991):
        self.loop, self.host, self.port = loop, host, port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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
            self.event_servers[EventHandler()] = 0

    async def getServer(self, servers):
        return min(servers, key = lambda i : servers[i])

    async def handle(self, c):
        server = await self.getServer(self.event_servers)
        self.event_servers[server] += 1
        await self.loop.create_task(server.handle(c))

    async def start(self):

        while not self.started:
            if await self.checkSocket(self.sock, self.host, self.port):
                self.started = True
                break
            print("failed")
            sleep(2)
            self.port += 1
        self.sock.listen()
        await self.spawnEventServer(2)
        print("server listening")
        while self.started:
            c, _ = self.sock.accept()
            await self.handle(c)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    gateway = Gateway(loop)

    loop.run_until_complete(gateway.start())
