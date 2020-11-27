from uuid import uuid4 as uuid

from auth import get_user, hash_password
from bson.objectid import ObjectId
from db import rooms_collection, users_collection
from flask import Blueprint, abort, jsonify, request

lobby_api = Blueprint("lobby_api", __name__)


def unjoined_room_projection():
    return {
        "_id": 1,
        "name": 1,
        "passworded": 1,
        "user_count_max": 1,
        "user_count": {"$size": "$states"},
    }


def joined_room_projection(user):
    return {
        "_id": 1,
        "name": 1,
        "play_time": 1,
        "passworded": 1,
        "user_count_max": 1,
        "user_count": {"$size": "$states"},
        "round": 1,
    }


@lobby_api.route("/rooms")
def rooms():
    # return available rooms
    rooms = list(rooms_collection.aggregate([  # get all rooms
        {"$project": unjoined_room_projection()}
    ]))
    if request.path == "/rooms":
        return jsonify(rooms)
    else:
        return rooms


@lobby_api.route("/joined_rooms")
def joined_rooms():
    # return user's joined rooms
    user = get_user()
    rooms = list(rooms_collection.aggregate([  # get a list of all rooms joined by user
        {"$match": {"_id": {"$in": user["rooms"]}}},
        {"$project": joined_room_projection(user)}
    ]))
    if request.path == "/joined_rooms":
        return jsonify(rooms)
    else:
        return rooms


@lobby_api.route("/create_room", methods=["GET", "POST"])
def create_room():
    # create new room
    # return room_id
    user = get_user()
    config = request.get_json()
    if config is None:  # check json was posted
        abort(400)
    if "name" not in config:  # check room name is in json
        abort(400)
    if "password" in config and len(config["password"]) > 0:  # if passworded room requested
        hashed, salt = hash_password(config["password"])  # hash password
        password = {"hash": hashed, "salt": salt}
    else:
        password = None  # else no password
    room = rooms_collection.insert_one(  # create room
        {
            "name": config["name"],
            "play_time": config.get("play_time", 45),
            "passworded": password is not None,
            "password": password,
            "user_count_max": config.get("user_count_max", 8),
            "states": [],
            "admins": [user["_id"]],
            "round": 0,
            "round_start_time": None,
            "caesar": None,
            "black": None,
            "round_ended": None,
            "winner": None,
            "used_white_cards": [],
            "used_black_cards": [],
        }
    )
    state = join_room(room.inserted_id, user=user)
    return jsonify({"room_id": room.inserted_id, "public_id": state["public_id"]})


def gen_empty_user_state(user, username=None):
    if username is None or len(username) == 0:
        username = "anon"  # "Mr. X"
    return {
        "user": user["_id"],
        "public_id": uuid(),
        "name": username,
        "cards_in_hand": None,
        "cards_on_table": [],
        "points": 0,
    }


@lobby_api.route("/join_room/<string:room_id>", methods=["GET", "POST"])
def join_room(room_id, user=None):
    # join a room
    if user is None:
        user = get_user()
    room = list(rooms_collection.aggregate([
        {"$match": {"_id": ObjectId(room_id)}},
        {"$addFields": {"user_count": {"$size": "$states"}}}
    ]))
    if len(room) == 0:  # check room exists
        abort(400)
    room = room[0]
    if room["user_count"] >= int(room["user_count_max"]):  # check if room is full
        abort(403)
    if room["_id"] not in user["rooms"]:  # check if room in user's rooms
        users_collection.update_one(
            {"_id": user["_id"]},
            {"$push": {
                "rooms": room["_id"],
            }}
        )
    if not any([user["_id"] == state["user"] for state in room["states"]]):  # check if user in room's states
        config = request.get_json()
        if config is None:  # check json was posted
            config = {}
        if room["passworded"] is not False:  # check if room passworded
            if "password" not in config:  # check password was sent
                abort(403)
            hashed, _ = hash_password(config["password"], room["password"]["salt"])
            if hashed != room["password"]["hash"]:  # check password
                abort(403)
        state = gen_empty_user_state(user=user, username=config.get("username", None))
        if len(room["admins"]) == 0:  # if there are no admins
            rooms_collection.update_one(  # add user to room and set it as admin
                {"_id": room["_id"]},
                {"$push": {
                    "admins": user["_id"],
                    "states": state,
                }}
            )
        else:
            rooms_collection.update_one(  # add user to room
                {"_id": room["_id"]},
                {"$push": {
                    "states": state,
                }}
            )
    if request.path.startswith("/join_room/"):
        return jsonify({"public_id": state["public_id"]})
    else:
        return state


@lobby_api.route("/leave_room/<string:room_id>")
def leave_room(room_id):
    # leave room
    user = get_user()
    room_id = ObjectId(room_id)
    if room_id not in user["rooms"]:  # check user in room
        abort(403)
    users_collection.update_one(
        {"_id": user["_id"]},
        {"$pull": {
            "rooms": room_id,
        }}
    )
    rooms_collection.update_one(
        {"_id": ObjectId(room_id)},
        {"$pull": {
            "states": {"user": user["_id"]},
            "admins": user["_id"],
        }}
    )
    # TODO: check if was last admin and set another user as admin
    return "OK", 200
