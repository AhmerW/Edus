import ssl
import asyncio
from sanic import Sanic
from sanic.response import json, text
from sanic.exceptions import ServerError, abort, NotFound

app = Sanic(__name__)
VERSION = 'v1'
MAIN_ROUTE = '/api/{0}/'.format(VERSION)

ROUTES = [
    '{0}messages/add/'
    '{0}login/',
    '{0}register/'
]
ROUTES = [route.format(MAIN_ROUTE) for route in ROUTES]

server = None

async def verifyToken(token):
    return False


@app.route(MAIN_ROUTE, methods=["POST"])
async def home(request):
    raise ServerError("Bad request", status_code=404)

@app.route(ROUTES[0], methods=["POST"])
async def messageAdd(request):
    data = request.json
    if not server:
        raise ServerError("Server offline", status_code=500)
    if not await verifyToken(data.get('token')):
        return json({"status": 404, "error": "Not authorized"})
    if not server.data.get(data['uid']):
        return json({"status": 404, "error": "Not authorized"})
    return json({"status": 200})


@app.route(ROUTES[1])
async def login(request):
    username, password = str(request.json.get('username')), str(request.json.get('password'))
    if not username.strip() or not password.strip():
        return json({"status": 404})


@app.exception(NotFound)
async def NotFoundException(request, exception):
    return text("Could not find the page matching your requirements.", status=500)


class MainApi(object):
    def __init__(self, _server):
        global server
        server = _server

    async def validateToken(self):
        pass

    async def start(self, *args, **kwargs) -> None:
        app.run(*args, **kwargs)

if __name__ == '__main__':
    api = MainApi(None)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(api.start('localhost', 8989))
