import aiohttp
import asyncio

API_VERSION = "v1"
API_IP = 'http://127.0.0.1'
API_PORT = 8989

class Calls(object):
    def __init__(self):
        self.session = aiohttp.ClientSession()
        self.url = '{0}:{1}/api/{2}/'.format(API_IP, API_PORT, API_VERSION)
        self.latest = 1
        self.latest_login = None



    async def getUrl(self, *urls):
        return "{0}{1}".format(self.url, '/'.join(urls))+"/"

    async def login(self, username, password):
        data = await self.basic('login', {"username": username, "password": password})
        print("got ", data)
        self.latest_login =  data
        return data

    async def register(self, username, password):
        return await self.basic('register', {"username": username, "password": password})

    async def basic(self, url, data):
        async with self.session.post(await self.getUrl(url), data=data) as resp:
            return await resp.json()

    async def sendMessage(self, msg, uid, name, tid):
        payload = {
            'content': msg,
            'uid': uid,
            'author': name,
            'target': tid # target id
        }
        try:
            async with self.session.post(await self.getUrl('messages','add'), json=payload) as resp:
                self.latest = True
                return await resp.json()
        except Exception as e:
            self.latest = False
