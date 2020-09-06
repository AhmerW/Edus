import aiohttp
import asyncio

API_VERSION = "v1"
API_IP = 'http://127.0.0.1'
API_PORT = 8989

class Calls(object):
    def __init__(self):
        self.session = aiohttp.ClientSession()
        self.url = '{0}:{1}/api/{2}/'.format(API_IP, API_PORT, API_VERSION)
    async def getUrl(self, *urls):
        return "{0}{1}".format(self.url, '/'.join(urls))+"/"

    async def sendMessage(self, msg, uid, name, tid):
        payload = {
            'content': msg,
            'uid': uid,
            'author': name,
            'target': tid # target id
        }
        try:
            async with self.session.post(await self.getUrl('messages','add'), json=payload) as resp:
                return await resp.json()
        except Exception as e:
            print(e)
            
