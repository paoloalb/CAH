from api import *
from auth import *
from flask import Flask, abort, send_file
from lobby_api import *
from website import *
from flask_babel import Babel, format_date, gettext

app = Flask(__name__)
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
babel = Babel(app)

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
    return 'it'


@app.route("/favicon.ico")
def favicon():
    return send_file("static/images/favicon.ico")


@app.route("/teapot")
def teapot():
    abort(418)
