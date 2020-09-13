import os
import ssl
import sys
import asyncio
import threading
from sanic import Sanic
from functools import wraps
from sanic.response import json, text
from sanic.exceptions import ServerError, abort, NotFound
from gateway import Gateway

app = Sanic(__name__)
VERSION = 'v1'
MAIN_ROUTE = '/api/{0}/'.format(VERSION)

ROUTES = [
    '{0}messages/add/'.format(MAIN_ROUTE),
    '{0}login/'.format(MAIN_ROUTE),
    '{0}register/'.format(MAIN_ROUTE),
    '{0}friend/add/'.format(MAIN_ROUTE)
]


server = Gateway()

def authorized(func):
    @wraps(func)
    async def deco(req, *args, **kwargs):
        uid, token = req.form.get('uid'), req.form.get('token')
        if not await server.auth.verify(uid, token):
            print("not authorized")
            return json({'status': 'not authorized'}, 403)
        print("authorized")
        return await func(req, *args, **kwargs)
    return deco

@app.listener('before_server_start')
async def before(sanic, loop):
    await server.run()


@app.route(MAIN_ROUTE, methods=["POST"])
@authorized
async def home(request):
    raise ServerError("Bad request", status_code=404)

@app.route(ROUTES[0], methods=["POST"])
@authorized
async def messageAdd(request):
    data = {k: v[0] if isinstance(v, list) else v for k, v in request.form.items()}
    data, stat = await server.auth.sendMessage(data)
    return json(data, 200 if stat else 404)


@app.route(ROUTES[1], methods=["POST"])
async def login(request):
    return json(await server.auth.verifyLogin(request.form))


@app.route(ROUTES[2], methods=["POST"])
async def register(request):
    return json(await server.auth.register(request.form))


async def checkUpdate(request):
    pass

@app.route(ROUTES[3], methods=["POST"])
async def friendRequest(request):
    return json(await server.auth.sendFriendRequest(request.form))

@app.exception(NotFound)
async def NotFoundException(request, exception):
    return text("Could not find the page matching your requirements.", status=500)





if __name__ == "__main__":
    if not len(sys.argv) > 1:
        sys.stdout.write('Console argument 1 must be database authentication\n')
    else:
        os.environ['pg_auth'] = sys.argv[1]
        app.run('localhost', 8989, debug=True)
