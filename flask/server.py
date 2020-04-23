from api import *
from flask import Flask
from website import *

app = Flask(__name__)

app.register_blueprint(api)
app.register_blueprint(website)
