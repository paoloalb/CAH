from api import *
from flask import Blueprint, render_template
from lobby_api import *
from flask import Flask, abort, send_file, render_template
from lobby_api import *
from website import *
from flask_babel import Babel, gettext


website = Blueprint("website", __name__)


@website.route("/")
def root():
    return render_template("index.html", rooms=rooms_info(), joined_rooms=joined_rooms_info())


@website.route("/room/<string:room_id>")
def room(room_id):
    return render_template("room.html",
                           room=room_info(room_id),
                           players=joined_room_players(room_id),
                           state=joined_room_state(room_id),
                           userRoom=init_user_page(room_id),
                           caesar = False
                           )
