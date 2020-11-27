import time

from auth import get_user
from bson.objectid import ObjectId
from db import cards_collection, rooms_collection
from flask import Blueprint, abort, jsonify, request

api = Blueprint("api", __name__)


def get_room(room_id, user=None):
    if user is None:
        user = get_user()
    room = list(rooms_collection.aggregate([
        {"$match": {"_id": ObjectId(room_id)}},
        {"$addFields": {"user_count": {"$size": "$states"}}}
    ]))
    if len(room) == 0:  # check room exists
        abort(400)
    room = room[0]
    user_in_states = [user["_id"] == state["user"] for state in room["states"]]
    if True in user_in_states:
        state = room["states"][user_in_states.index(True)]
    else:
        state = None
    if state is None or room["_id"] not in user["rooms"]:  # check if user in room's states
        abort(403)
    return room, state


def has_round_ended(room, t=None):
    # Returns True if round ended
    if room["round_start_time"] is None:
        return True
    if t is None:
        t = time.time()
    return room["round_ended"] or t > room["round_start_time"] + room["play_time"]


def pick(room, card_type, n=1):
    if card_type == "white":
        cards = list(cards_collection.aggregate([
            {"$match": {
                "_id": {"$nin": room["used_white_cards"]},
                "$or": [{"pick": {"$exists": False}}, {"pick": None},  {"pick": 0}],
            }},
            {"$sample": {"size": n}},
            {"$project": {"_id": 1}},
        ]))
    elif card_type == "black":
        cards = list(cards_collection.aggregate([
            {"$match": {
                "_id": {"$nin": room["used_black_cards"]},
                "pick": {"$gt": 0}
            }},
            {"$sample": {"size": n}},
        ]))
    else:
        raise AssertionError("no such card type: {}".format(card_type))
    if len(cards) == n:
        cards = list(cards)
    else:
        cards = None
    return cards


@api.route("/players/<string:room_id>")
def players(room_id):
    # Returns current white card Ids and text in the user hand
    room, state = get_room(room_id)
    states = [{k: state[k] for k in ["public_id", "name", "points"]} for state in room["states"]]
    return jsonify(states)


@api.route("/new_round/<string:room_id>", methods=["GET", "POST"])
def new_round(room_id):
    # Starts a new round
    room, state = get_room(room_id)
    round_ended = has_round_ended(room)
    if not round_ended and state["user"] not in room["admins"]:  # check round ended or admin skipped round
        abort(403)
    # pick a random black card
    black_cards = pick(room, "black", 1)
    if black_cards is None:
        # put used black cards back in deck if not on table
        room["used_black_cards"] = [room["black"]["_id"]]
        # pick a random black card
        black_cards = pick(room, "black", 1)
        if black_cards is None:
            print("could not find black unused cards", flush=True)
            abort(500, "could not find black unused cards")
    room["used_black_cards"] += [card["_id"] for card in black_cards]
    # deal white cards to players
    cards_in_hands = []
    for s in room["states"]:
        if s["cards_in_hand"] is None:
            s["cards_in_hand"] = []
        if round_ended:
            cards_in_hand = s["cards_in_hand"]
        else:
            cards_in_hand = s["cards_in_hand"] + s["cards_on_table"]
        # remove player cards from table
        s["cards_on_table"] = []
        cards_in_hands += cards_in_hand
    needed_cards = (len(room["states"]) * 7) - len(cards_in_hands)
    white_cards = pick(room, "white", needed_cards)
    if white_cards is None:
        # put used white cards back in deck if not in hands
        room["used_white_cards"] = cards_in_hands
        # pick a random black card
        white_cards = pick(room, "white", needed_cards)
        if white_cards is None:
            print("could not find white unused cards", flush=True)
            abort(500, "could not find white unused cards")
    room["used_white_cards"] += white_cards
    for s in room["states"]:
        s["cards_in_hand"] += [white_cards.pop()["_id"] for i in range(7 - len(s["cards_in_hand"]))]
    # update room
    room.update({
        "round": room["round"] + 1,
        "round_start_time": time.time(),
        "caesar": room["states"][room["round"] % len(room["states"])]["public_id"],
        "black": black_cards[0],
        "round_ended": False,
        "winner": None,
    })
    rooms_collection.replace_one(
        {"_id": ObjectId(room_id)},
        room
    )
    return "OK", 200


@api.route("/hand/<string:room_id>")
def hand(room_id):
    # Returns current white card Ids and text in the user hand
    room, state = get_room(room_id)
    cards = list(cards_collection.find(
        {"_id": {"$in": state["cards_in_hand"] + state["cards_on_table"]}},
        {
            "_id": 1,
            "text": 1,
        }
    ))
    return jsonify(cards)


@api.route("/table/<string:room_id>")
def table(room_id):
    # Returns current white card Ids and text in the user hand
    room, state = get_room(room_id)
    cards = []
    for s in room["states"]:
        cards += s["cards_on_table"]
        if s["public_id"] == room["caesar"]:
            caesar = s
    t = time.time()
    if not has_round_ended(room, t):  # check round ended
        cards = len(cards)
        t -= room["play_time"]
    else:
        cards = list(cards_collection.find(
            {"_id": {"$in": cards}},
            {
                "_id": 1,
                "text": 1,
                "pick": 1,
            }
        ))
    table = {
        "round": room["round"],
        "time_left": room["play_time"] - (t - room["round_start_time"]),
        "black": room["black"],
        "caesar": caesar["public_id"],
        "cards": cards,
        "round_ended": room["round_ended"],
        "winner": room["winner"],
    }
    return jsonify(table)


@api.route("/play_cards/<string:room_id>", methods=["GET", "POST"])
def play_cards(room_id):
    # Takes a list of card ids and moves them from the player's hand to the table
    room, state = get_room(room_id)
    round_ended = has_round_ended(room)
    if round_ended:  # check round not ended
        abort(403)
    if state["public_id"] == room["caesar"]:  # check if user is caezar
        abort(403)
    config = request.get_json()
    if config is None or "cards" not in config or type(config["cards"]) is not list:  # check json config
        abort(400)
    if len(config["cards"]) != room["black"]["pick"]:  # check number of cards submitted
        abort(400)
    cards = [ObjectId(card) for card in config["cards"]]
    if any([card not in state["cards_in_hand"] for card in cards]):  # check user has played cards
        abort(403)
    everybody_played = all([len(s["cards_on_table"]) > 0 or s["cards_in_hand"] is None for s in room["states"] if s["public_id"] != room["caesar"] and s["user"] != state["user"]])  # check if all others played
    # put player's cards on table and end round if needed
    rooms_collection.update_one(
        {
            "_id": room["_id"],
            "states.user": state["user"],
        },
        {
            "$pull": {"states.$.cards_in_hand": {"$in": cards}},
            "$set": {
                "states.$.cards_on_table": cards,
                "states.$.played": True,
                "round_ended": round_ended or everybody_played,
            },
        }
    )
    return "OK", 200


@api.route("/card_wins/<string:room_id>/<string:card_id>")
def card_wins(room_id, card_id):
    # Grants a point to the winner
    room, state = get_room(room_id)
    if state["public_id"] != room["caesar"]:  # check if user is caezar
        abort(403)
    if not has_round_ended(room):  # check round ended
        abort(403)
    # get winning player
    winner = None
    card_id = ObjectId(card_id)
    for state in room["states"]:
        if card_id in state["cards_on_table"]:
            winner = state
    if winner is None:  # check if winner exists
        abort(409)
    # update round winner and winner points
    rooms_collection.update_one(
        {
            "_id": room["_id"],
            "states.user": winner["user"],
        },
        {
            "$set": {
                "winner": {
                    "public_id": winner["public_id"],
                    "cards": list(cards_collection.find({"_id": {"$in": winner["cards_on_table"]}})),
                }
            },
            "$inc": {"states.$.points": 1},
        }
    )
    return "OK", 200


# --------------------------------------------------


@api.route("/init_user_page/<string:my_room_id>")
# create a class with all user date for start the game
# TODO missing info about who is the ceaser
def init_user_page(my_room_id):
    users = user_list(my_room_id)
    white_cards = random_white_cards_test(14)
    black_cards = random_black_card(my_room_id)
    dict_to_print = dict({"users": users, "white_cards": white_cards, "black_cards": black_cards})
    return dict_to_print
