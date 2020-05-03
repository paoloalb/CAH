from api import *
from cookies import *
from flask import Flask, abort, send_file
from lobby_api import *
from website import *

app = Flask(__name__)


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


app.json_encoder = JSONEncoder

app.register_blueprint(cookies)
app.register_blueprint(api)
app.register_blueprint(lobby_api)
app.register_blueprint(website)


@app.route("/favicon.ico")
def favicon():
    return send_file("static/images/favicon.ico")


@app.route("/teapot")
def teapot():
    abort(418)
