import ssl
import asyncio
import threading
from sanic import Sanic
from sanic.response import json, text
from sanic.exceptions import ServerError, abort, NotFound
from gateway import Gateway

app = Sanic(__name__)
VERSION = 'v1'
MAIN_ROUTE = '/api/{0}/'.format(VERSION)

ROUTES = [
    '{0}messages/add/'.format(MAIN_ROUTE),
    '{0}login/'.format(MAIN_ROUTE),
    '{0}register/'.format(MAIN_ROUTE)
]


server = Gateway()

async def verifyToken(token):
    return False

def func():
    print("hi")

@app.listener('before_server_start')
async def before(sanic, loop):
    await server.run()


@app.route(MAIN_ROUTE, methods=["POST"])
async def home(request):
    raise ServerError("Bad request", status_code=404)

@app.route(ROUTES[0], methods=["POST"])
async def messageAdd(request):
    data = request.form
    if not server:
        raise ServerError("Server offline", status_code=500)
    if not await verifyToken(data.get('token')):
        return json({"status": 404, "error": "Not authorized"})
    if not server.data.get(data['uid']):
        return json({"status": 404, "error": "Not authorized"})
    return json({"status": 200})


@app.route(ROUTES[1], methods=["POST"])
async def login(request):
    return json(await server.auth.verifyLogin(request.form))


@app.route(ROUTES[2], methods=["POST"])
async def register(request):
    return json(await server.auth.register(request.form))

@app.exception(NotFound)
async def NotFoundException(request, exception):
    return text("Could not find the page matching your requirements.", status=500)





if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    app.run('localhost', 8989, debug=True)
