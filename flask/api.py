import json
import sys
from bson.objectid import ObjectId
from bson.son import SON
from pymongo import MongoClient

from cookies import get_cookie
from flask import (Blueprint, abort, jsonify, make_response, render_template,
                   request)
from hasher import *

api = Blueprint('api', __name__, )

client = MongoClient("mongodb+srv://paoloa:123stella@mflix-3d6kd.mongodb.net/test")
db = client["cah"]
cards_collection = db["cards"]
rooms_collection = db["rooms"]
users_collection = db["users"]


@api.route('/new_room', methods=['GET', 'POST'])
def create_room():
    config = request.get_json()
    user_cookie = get_cookie()
    if "password" in config and len(config["password"]) > 0:
        hashed, salt = hash_password(config["password"])
        password = {"hash": hashed, "salt": salt}
    else:
        password = None
    room = rooms_collection.insert_one(
        {
            "name": config["name"],
            "black": None,
            "caesar": None,
            "n_of_users": 0,
            "users": [],
            "used_cards": [],
            "round": 0,
            "admins": [],
            "password": password,
            "max_n_of_players": 5
        }
    )
    return jsonify({"room_id": str(room.inserted_id)})


@api.route('/join_room/<string:room_id>/<string:username>')
def create_state(room_id, username):
    # Returns the ID of the user as a string
    user_cookie = get_cookie()
    if username is None or len(username) == 0:
        # username = "Mr. X"
        username = "anon"

    room = rooms_collection.find_one({"_id": ObjectId(room_id)})

    if room["n_of_users"] >= room["max_n_of_players"]:  # Check if room is full
        abort(403)

    finduser = users_collection.find_one({"cookie": user_cookie, "room": ObjectId(room_id)})

    if finduser is not None:
        abort(403)

    user = users_collection.insert_one(
        {
            "cookie": user_cookie,
            "name": username,
            "room": ObjectId(room_id),
            "cards_in_hand": [],
            "cards_on_table": [],
            "points": 0
        }
    )
    if len(room["users"]) == 0:
        rooms_collection.update_one(
            {
                "_id": ObjectId(room_id),
            },
            {
                "$push": {
                    "users": user.inserted_id,
                    "admins": user.inserted_id,
                },
                "$inc": {
                    "n_of_users": 1,
                },
            }
        )
    else:
        rooms_collection.update_one(
            {
                "_id": ObjectId(room_id),
            },
            {
                "$push": {
                    "users": user.inserted_id,
                },
                "$inc": {
                    "n_of_users": 1,
                },
            }
        )
    return make_response("OK", 200)


@api.route('/rooms')
def rooms():
    # returns available rooms
    user_cookie = get_cookie()
    rooms = rooms_collection.find()
    if request.path != "/rooms":
        return rooms
    else:
        return jsonify({"rooms": rooms})


@api.route('/my_rooms')
def user_rooms():
    # given the cookie, returns all about his rooms
    user_cookie = get_cookie()
    states = list(users_collection.find(
        {
            "cookie": user_cookie,
        },
        {
            "_id": 1,
        }
    ))
    rooms = list(rooms_collection.find(
        {
            "users": {
                "$in": [state["_id"] for state in states],
            },
        }
    ))
    if request.path != "/my_rooms":
        return rooms
    else:
        return jsonify({"rooms": rooms})


@api.route('/my_room_status/<string:room_id>')
def user_room_state(room_id):
    # given cookie and room id, return all info about user
    user_cookie = get_cookie()
    state = users_collection.find_one(
        {
            "cookie": {
                "$eq": user_cookie,
            },
            "room": ObjectId(room_id),
        }
    )
    return jsonify(state)


@api.route('/teapot')
def teapot():
    abort(418)


# just for test it should be add user cookie and room id
@api.route('/randomWhiteCards/<int:number_of_cards>')
def random_white_cards_test(number_of_cards):
    pipeline = [
        {"$match": {"pick": 0}},
        {"$sample": {"size": number_of_cards}}
    ]
    cards = list(cards_collection.aggregate(pipeline))
    return cards


@api.route('/randomWhiteCards/<string:my_room_id>/<int:number_of_cards>')
def random_white_cards(number_of_cards, my_room_id):
     user_cookie = get_cookie()
     my_user_id = users_collection.find_one({"cookie": user_cookie, "room": ObjectId(my_room_id)})["_id"]
     list_of_used_cards = rooms_collection.find_one({"_id": ObjectId(my_room_id)})["used_cards"]
     pipeline = [
         {"$match": {"pick": 0, "_id": {"$nin": list_of_used_cards}}},
         {"$sample": {"size": number_of_cards}}
     ]
     cards = list(cards_collection.aggregate(pipeline))

     rooms_collection.update_one({"_id": ObjectId(my_room_id)},
                                {"$push":
                                {"used_cards": {"$each": [c["_id"] for c in cards]}}
                                })

     users_collection.update_one({"_id": ObjectId(my_user_id)},
                                {"$push":
                                {"cards_in_hand": {"$each": [c["_id"] for c in cards]}}
                                })

     return jsonify(cards) # if i want only text : return jsonify({"cards": [c["text"] for c in cards]})


# just for test it should be add user cookie and room id
@api.route('/randomBlackCardTest')
def random_black_card_test():
    pipeline = [
        {"$match": {"pick": {"$gt": 0}}},
        {"$sample": {"size": 1}}
    ]

    card = list(cards_collection.aggregate(pipeline))
    return card


@api.route('/randomBlackCard/<string:my_room_id>')
def random_black_card(my_room_id):
    pipeline = [
        {"$match": {"pick": {"$gt": 0}}},
        {"$sample": {"size": 1}}
    ]

    card = cards_collection.aggregate(pipeline).next()

    rooms_collection.update_one(
                                {"_id": ObjectId(my_room_id)},
                                {"$push": {"used_cards": card["_id"]},
                                "$set": { "black":  card["_id"]} }
                                )

    return card


@api.route('/play_cards/<string:my_room_id>')
def play_cards(my_room_id, list_of_card_ids):
    user_cookie = get_cookie()
    my_user_id = users_collection.find_one({"cookie": user_cookie, "room": ObjectId(my_room_id)})["_id"]
    for card in list_of_card_ids:
        my_card = users_collection.find_one(
                                            {"_id": ObjectId(my_user_id),
                                            "cards_in_hand": ObjectId(card)}
                                            )
        if my_card is None:  # Make sure that the card is in the hand of the user
            abort(403)  # If not, forbidden error

    for card in list_of_card_ids:
        # remove card from player's hand and put it on the table
        users_collection.update_one({"_id": ObjectId(user_id)},
                                    {
                                    "$pull": {"cards_in_hand": ObjectId(card)},
                                    "$push": {"cards_on_table": ObjectId(card)}})
    return make_response("OK", 200)



@api.route('/user_wins/<string:my_room_id>')
def user_wins(my_room_id):
    user_cookie = get_cookie()
    my_user_id = users_collection.find_one({"cookie": user_cookie, "room": ObjectId(my_room_id)})
    if my_user_id is None:  # Make sure that the user exists
        abort(403)
    users_collection.update_one({"_id": ObjectId(my_user_id["_id"])}, {"$inc": {"points": 1}})
    return make_response("OK", 200)
