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
        return "{0}{1}/".format(self.url, '/'.join(urls))



    async def basic(self, data, *urls):
        try:
            async with self.session.post(await self.getUrl(*urls), data=data) as resp:
                return await resp.json()
        except Exception as e:
            return {}

    async def sendMessage(self, msg, uid, name, tid, tn, token):
        payload = {
            'content': msg,
            'uid': uid,
            'author': name,
            'target': tid, # target id,
            'target_name': target_name
            'type': 'dm',
            'token': token

        try:
            return await self.basic(payload, 'messages','add')
        except Exception as e:
            self.latest = False
