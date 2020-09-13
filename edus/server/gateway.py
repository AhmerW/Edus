import os
import json
import socket
import asyncio
import threading
import asyncpg
from time import sleep
from handler import EventHandler
from security.gen import randUid, randToken


UID_LEN = 12
TOKEN_LEN = 20

## QUERIES ##
LOGIN_QUERY = "select uid, token, username, friends from users where email=$1 and password=$2"
REGISTER_QUERY = """insert into users(uid, email, password, username, token) values($1, $2, $3, $4, $5)"""
class Auth(object):
    def __init__(self, pool):
        self.pool = pool
        self.db = {} # uid : {}
        self.userdb = {} # email: uid
        self.conn = None

    async def clear(self, data, index=0):
        if len(data) == 0:
            return {}
        return {k: v for k, v in data[index].items()}

    async def verify(self, uid, token):
        uid = int(uid) if uid.isdigit() else None
        if not self.db.get(uid):
            return False
        return self.db[uid]['token'] == token

    async def checkExists(self, email):
        async with self.pool.acquire() as con:
            res = await con.fetch('select * from users where email=$1', email)
            print("email ", res)
            return bool(res)

    async def sendFriendRequest(self, data):
        author, target = data.get('from'), data.get('target')
        invalid = {'status': False, 'message': None}
        if not author.isdigit() or not target.isdigit():
            return invalid
        author, target = int(author), int(target)

        if not self.db.get(author):
            return invalid

        if target in self.db.get(author)['relations']['friends']:
            return {'status': False, 'message': 'Already friends'}
        self.db['author']['relations']['friends'][target] = data.get('target_name')

    async def sendMessage(self, data):
        invalid = {'message': 'not sent'}, False
        uid = data.get('uid')

        if not self.db.get(uid):
            return invalid

        target = data.get('target')
        mtype = data.get('type')

        if mtype == 'dm':
            if not target in self.db[uid]['relations']['friends']:
                print("target not a friend")
                return invalid
            if not target in self.db:
                print("target not online")
                return invalid
            sock = self.db[target]['client']
            if sock:
                print("sent to sock")
                sock.send('{0}:{1}'.format('on_message', data.get('content')))
                return {'message': 'sent'}, True
        return invalid


    async def verifyLogin(self, data):
        email, password = data.get('email'), data.get('password')

        async with self.pool.acquire() as con:
            res = await con.fetch(
                LOGIN_QUERY,
                email,
                password
            )
            res = await self.clear(res)

        uid, token = res.get('uid'), res.get('token')
        username, friends = res.get('username'), res.get('friends')
        if not self.db.get(uid):
            self.db[uid] = {
                    'token': token,
                    'client': None,
                    'relations': {'friends': json.loads(friends.replace("'", ""))}
                }

        return {
                'status': bool(res),
                'uid': uid,
                'token': token,
                'username': username
            }

    async def register(self, data):
        username, password = data.get('username'), data.get('password')
        email = data.get('email')
        print("registering with ", data)
        if self.userdb.get(email) or not email:
            return {'uid': None}
        if await self.checkExists(email):
            return {'status': False, 'uid': None}

        uid = randUid(UID_LEN)
        token = randToken(TOKEN_LEN)

        async with self.pool.acquire() as con:
            await con.execute(REGISTER_QUERY, uid, email, password, username, str(token))

        self.userdb[email] = uid
        self.db[uid] = {
                'token': token,
                'client': None,
                'relations': {'friends': {}} # uid, name
            }

        return {'uid': uid, 'token': token}

class Gateway():
    def __init__(self, host = 'localhost', port = 8991):
        self.host, self.port = host, port
        self.loop = asyncio.get_event_loop()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.auth = None
        self.pool = None

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
        tasks = []
        task = await self.loop.create_task(server.handle(c))
        if task:
            tasks.append(task)
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
        self.pool = await asyncpg.create_pool(
            user='postgres',
            password=os.getenv('pg_auth'),
            host='127.0.0.1',
            database='edus'
        )
        self.auth = Auth(self.pool)
        await self.spawnEventServer(2)
        self.sock.listen()
        threading.Thread(target=self.actual).start()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    gateway = Gateway(loop)

    loop.create_task(gateway.start())
