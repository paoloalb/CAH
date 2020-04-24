from api import *
from cookies import *
from flask import Flask, abort, url_for
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
app.register_blueprint(website)


@app.route('/favicon.ico')
def favicon():
    return send_file('static/favicon.ico')
