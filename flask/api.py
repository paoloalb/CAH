import json
import sys

from bson.objectid import ObjectId

from cookies import get_cookie
from db import *
from flask import Blueprint, abort, jsonify, make_response, request

api = Blueprint('api', __name__, )


@api.route('/my_room_status/<string:room_id>')
def user_room_state(room_id):
    # given cookie and room id, return all info about user
    user_cookie = get_cookie()
    state = users_collection.find_one(
        {
            "cookie": user_cookie,
            "room": ObjectId(room_id),
        }
    )
    return jsonify(state)


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
    # Updates user's hand, used card list and returns the picked cards in a json format
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

    return jsonify(cards)  # if i want only text : return jsonify({"cards": [c["text"] for c in cards]})


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
         "$set": {"black": card["_id"]}}
    )

    return card


@api.route('/play_cards/<string:my_room_id>', methods=['GET', 'POST'])
def play_cards(my_room_id):
    # Takes a list of card Ids and move the cards from the player's hand to the table
    config = request.get_json()
    list_of_card_ids = config["list"]
    user_cookie = get_cookie()
    my_user_id = users_collection.find_one({"cookie": user_cookie, "room": ObjectId(my_room_id)})["_id"]

    for card in list_of_card_ids:
        my_card = users_collection.find_one(
            {"_id": my_user_id,
             "cards_in_hand": ObjectId(card)}
        )
        if my_card is None:  # Make sure that the card is in the hand of the user
            abort(403)  # If not, forbidden error

    for card in list_of_card_ids:
        # remove card from player's hand and put it on the table
        users_collection.update_one({"_id": my_user_id},
                                    {
                                        "$pull": {"cards_in_hand": ObjectId(card)},
                                        "$push": {"cards_on_table": ObjectId(card)}})
    return make_response("OK", 200)


@api.route('/user_wins/<string:my_room_id>')
def user_wins(my_room_id):
    # Grants a point to the winner and deletes all the cards from the table
    user_cookie = get_cookie()
    my_user_id = users_collection.find_one({"cookie": user_cookie, "room": ObjectId(my_room_id)})
    if my_user_id is None:  # Make sure that the user exists with this cookie
        abort(403)
    # Update the points of the user
    users_collection.update_one({"_id": ObjectId(my_user_id["_id"])},
                                {"$inc": {"points": 1}})
    # Remove all the cards on the table:
    users_collection.update({"room": ObjectId(my_room_id)},
                            {"$set": {"cards_on_table": []}},
                            multi=True)
    return make_response("OK", 200)


@api.route('/current_white/<string:my_room_id>')
def current_white(my_room_id):
    # Returns current white card Ids and text in the user hand
    user_cookie = get_cookie()
    my_card_ids = users_collection.find_one({"cookie": user_cookie,
                                             "room": ObjectId(my_room_id)},
                                            {"cards_in_hand": 1})

    my_cards = list(cards_collection.find({"_id": {"$in": my_card_ids["cards_in_hand"]}}, {"text": 1}))
    return jsonify(my_cards)


@api.route('/current_black/<string:my_room_id>')
def current_black(my_room_id):
    # Returns everything about the current black card on the table as a json
    black_id = rooms_collection.find_one({"_id": ObjectId(my_room_id)},
                                         {"black": 1})
    black = cards_collection.find_one({"_id": black_id["black"]})
    return jsonify(black)


@api.route('/user_list/<string:my_room_id>')
# Returns a list with all the informations about users in the room
def user_list(my_room_id):
    users = list(users_collection.find({"room": ObjectId(my_room_id)}))
    return users


@api.route('/init_user_page/<string:my_room_id>')
# create a class with all user date for start the game
def init_user_page(my_room_id):
    users = user_list(my_room_id)
    white_cards = random_white_cards_test(14)
    black_cards = random_black_card(my_room_id)
    dict_to_print = dict({'users': users, 'white_cards': white_cards, 'black_cards': black_cards})

    return dict_to_print
