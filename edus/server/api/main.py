import ssl
import asyncio
import threading
from sanic import Sanic
from sanic.response import json, text
from sanic.exceptions import ServerError, abort, NotFound

app = Sanic(__name__)
VERSION = 'v1'
MAIN_ROUTE = '/api/{0}/'.format(VERSION)

ROUTES = [
    '{0}messages/add/'.format(MAIN_ROUTE),
    '{0}login/'.format(MAIN_ROUTE),
    '{0}register/'.format(MAIN_ROUTE)
]


server = None
print(ROUTES)

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


@app.route(ROUTES[1], methods=["POST"])
async def login(request):
    username, password = str(request.form.get('username')), str(request.form.get('password'))
    print("req")
    if not username.strip() or not password.strip():
        return json({"status": 404})
    return json({"status": await server.auth.verifyLogin(username, password)})


@app.route(ROUTES[2])
async def register(request):
      return json({
        "status": await server.auth.register(
            request.form.get('username'),
            request.form.get('password')
        )
      })

@app.exception(NotFound)
async def NotFoundException(request, exception):
    return text("Could not find the page matching your requirements.", status=500)



async def run(*args, **kwargs) -> None:
    app.run(*args, **kwargs)


if __name__ == "__main__":
    app.run('localhost', 8989)
