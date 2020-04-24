from api import *
from flask import Flask, url_for
from website import *

app = Flask(__name__)


app.register_blueprint(api)
app.register_blueprint(website)


@app.route('/favicon.ico')
def favicon():
    return url_for('static', filename='favicon.ico')


@app.route('/biscottini', methods=['POST', 'GET'])
def setcookie():
    resp = make_response(render_template('readcookie.html'))
    resp.set_cookie('userID', user)
    return resp


@app.route('/getcookie')
def getcookie():
    name = request.cookies.get('userID')
    return '<h1>welcome ' + str(name) + '</h1>'
