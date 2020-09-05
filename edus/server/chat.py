import asyncio
import websockets

async def hello(websocket, path):
    name = await websocket.recv()
    print(f"< {name}")

    greeting = f"Hello {name}!"

    await websocket.send(greeting)
    print(f"> {greeting}")

class ServerChat(object):
    def __init__(self, ip, port):
        self.ip, self.port = ip, port

    async def start(self, s, path):
        pass

server = ServerChat("localhost", 8180)

start_server = websockets.serve(server.start, server.ip, server.port)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
