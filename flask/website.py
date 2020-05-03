from api import *
from flask import Blueprint, render_template
from lobby_api import *

website = Blueprint("website", __name__, )


@website.route("/")
def root():
    return render_template("index.html", rooms=rooms_info(), joined_rooms=joined_rooms_info())


@website.route("/room/<string:room_id>")
def room(room_id):
    return render_template("room.html", room=room_info(room_id), state=joined_room_state(room_id))


@website.route("/UserPage/<string:room_id>")
def UserPage(room_id):
    return render_template("UserPage.html", userRoom=  init_user_page(room_id))
