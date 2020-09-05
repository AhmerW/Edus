from sanic import Sanic
from sanic.response import json

app = Sanic(__name__)
VERSION = 'v1'
ROUTES = [
    '/api/{0}/'.format(VERSION)
]

data = {}

@app.route(ROUTES[0])
async def home(request):
    return json({"hello": 10})

class MainApi(object):
    def __init__(self, _data):
        global data
        data = _data

    def start(self, *args, **kwargs):
        app.run(*args, **kwargs)
