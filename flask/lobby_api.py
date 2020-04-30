import json
import sys

from bson.objectid import ObjectId

from api import *
from cookies import get_cookie
from db import *
from flask import (Blueprint, abort, jsonify, make_response, redirect,
                   render_template, request, url_for)
from hasher import *

lobby_api = Blueprint('lobby_api', __name__, )


@lobby_api.route('/my_room_info/<string:room_id>')
def joined_room_state(room_id):
    # return user's room info
    # only accessible to joined users
    user_cookie = get_cookie()
    state = users_collection.find_one({"room": ObjectId(room_id), "cookie": user_cookie})
    if request.path.startswith("/my_room_status/"):
        if state is None:  # check if user joined
            abort(403)
        return jsonify(state)
    else:
        return state


@lobby_api.route('/room_info/<string:room_id>')
def room_info(room_id):
    # return room's info
    # accessible by anyone
    room = rooms_collection.find_one(  # get room's info
        {
            "room": ObjectId(room_id)
        },
        {
            "_id": 1,
            "name": 1,
            "user_count": 1,
            "round": 1,
            "password": 1,
            "user_count_max": 1,
        }
    )
    if request.path.startswith("/my_room_status/"):
        return jsonify(room)
    else:
        return room


@lobby_api.route('/rooms_info')
def rooms_info():
    # return rooms
    # accessible by anyone
    user_cookie = get_cookie()
    rooms = list(rooms_collection.find(  # get all rooms
        {},
        {
            "_id": 1,
            "name": 1,
            "user_count": 1,
            "round": 1,
            "password": 1,
            "user_count_max": 1,
        }
    ))
    if request.path == "/rooms":
        return jsonify({"rooms": rooms})
    else:
        return rooms


@lobby_api.route('/my_rooms_info')
def joined_rooms_info():
    # return user's joined rooms
    user_cookie = get_cookie()
    states = list(users_collection.find(  # get a list of all states._id of the user
        {
            "cookie": user_cookie,
        },
        {
            "_id": 1,
        }
    ))
    print(states, flush=True)
    rooms = list(rooms_collection.find(  # get all rooms' info of the user's joined rooms
        {
            "users": {
                "$in": [state["_id"] for state in states],
            },
        },
        {
            "_id": 1,
            "name": 1,
            "user_count": 1,
            "round": 1,
            "password": 1,
            "user_count_max": 1,
        }
    ))
    print(rooms, flush=True)
    if request.path == "/my_rooms_info":
        return jsonify({"rooms": rooms})
    else:
        return rooms


@lobby_api.route('/new_room', methods=['GET', 'POST'])
def create_room():
    # create new room
    # TODO: given parameters
    # return room_id
    config = request.get_json()
    if config is None:  # check json was posted
        abort(400)
    user_cookie = get_cookie()
    if "password" in config and len(config["password"]) > 0:  # if passworded room requested
        hashed, salt = hash_password(config["password"])  # hash password
        password = {"hash": hashed, "salt": salt}
    else:
        password = None  # else no password
    room = rooms_collection.insert_one(  # create room
        {
            "name": config["name"],
            "users": [],
            "admins": [],
            "round": 0,
            "black": None,
            "caesar": None,
            "used_cards": [],
            "user_count": 0,
            "user_count_max": 5,
            "password": password,
        }
    )
    return jsonify({"room_id": str(room.inserted_id)})


@lobby_api.route('/join_room/<string:room_id>/<string:username>', methods=['GET', 'POST'])
def join_room(room_id, username):
    # join a room
    # success: go to room
    # fail: 403
    user = joined_room_state(room_id)
    if user is None:
        room = rooms_collection.find_one({"_id": ObjectId(room_id)})
        if room is None:  # check room exists
            abort(400)
        if room["user_count"] >= room["user_count_max"]:  # check if room is full
            abort(403)
        print(room, flush=True)
        if room["password"] is not None:  # check if room passworded
            j = request.get_json()
            if "password" not in j or len(j["password"]) == 0:  # check password was sent
                abort(403)
            hash = room["password"]["hash"]
            salt = room["password"]["salt"]
            password = j["password"]
            if hash != hash_password(password, salt):  # check password
                abort(403)
        user_cookie = get_cookie()
        if username is None or len(username) == 0:
            username = "anon"  # "Mr. X"
        user = users_collection.insert_one(  # add user state
            {
                "cookie": user_cookie,
                "name": username,
                "room": ObjectId(room_id),
                "cards_in_hand": [],
                "cards_on_table": [],
                "points": 0
            }
        )
        if len(room["users"]) == 0:  # if room empty
            rooms_collection.update_one(  # add user to room and set first user as admin
                {
                    "_id": ObjectId(room_id),
                },
                {
                    "$push": {
                        "users": user.inserted_id,
                        "admins": user.inserted_id,
                    },
                    "$inc": {
                        "user_count": 1,
                    },
                }
            )
        else:
            rooms_collection.update_one(  # add user to room
                {
                    "_id": ObjectId(room_id),
                },
                {
                    "$push": {
                        "users": user.inserted_id,
                    },
                    "$inc": {
                        "user_count": 1,
                    },
                }
            )
    return redirect(url_for("website.room", room_id=room_id), 307)


@lobby_api.route('/leave_room/<string:room_id>')
def leave_room(room_id):
    # leave room
    # success: go to /
    # fail: go to /
    user_cookie = get_cookie()
    user = users_collection.find_one_and_delete(
        {
            "room": ObjectId(room_id),
            "cookie": user_cookie
        }, {"_id": 1, "room": 1})  # if user state exists delete it
    if user is not None:  # if user was in the room
        rooms_collection.update_one(  # remove user from room
            {
                "_id": ObjectId(user["room"]),
            },
            {
                "$pull": {
                    "users": user["_id"],
                    "admins": user["_id"],
                },
                "$inc": {
                    "user_count": -1,
                },
            }
        )
    return redirect(url_for("website.root"), 307)
