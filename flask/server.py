import json
import secrets

from api import api
from auth import auth
from bson.objectid import ObjectId
from flask import Flask, abort, request, send_file, session
from flask_babel import Babel
from flask_socketio import SocketIO
from lobby_api import lobby_api
from website import website

app = Flask(__name__)
app.secret_key = secrets.token_hex(256)  # for session
app.config["SECRET_KEY"] = secrets.token_hex(256)  # for socketio
socketio = SocketIO(app)
socketio.run(app)
app.config["BABEL_DEFAULT_LOCALE"] = "en"
babel = Babel(app)

LANGUAGES = {
    "en": "English",
    "it": "Italiano"
}


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


app.json_encoder = JSONEncoder

app.register_blueprint(auth)
app.register_blueprint(api)
app.register_blueprint(lobby_api)
app.register_blueprint(website)


@babel.localeselector
def get_locale():
    if request.args.get("lang"):
        session["lang"] = request.args.get("lang")
    return session.get("lang", "it")


@app.route("/favicon.ico")
def favicon():
    return send_file("static/images/favicon.ico")


@app.route("/teapot")
def teapot():
    abort(418)
