import aiohttp
import asyncio

API_VERSION = 1
API_IP = 'localhost'
API_PORT = 8989

class Calls(object):
    def __init__(self):
        self.session = aiohttp.ClientSession()
        self.url = '{0}/api/{1}/'.format(API_IP, API_VERSION)
    async def getUrl(self, *args):
        return "{0}{1}".format(self.url, '/'.join(args))

    async def sendMessage(self, msg, uid, name, cid, cname):
        payload = {
            'content': msg,
            'uid': uid,
            'cid': cid,
            'author': name,
            'channel': cname
        }
        async with self.session.post(self.getUrl('messages','add'), data=payload) as resp:
            if resp.status != 200:
                return {}
            return await resp.json()
