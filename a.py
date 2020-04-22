# DB SCHEMA

db = {
    "room": {
        "_id": 0,
        "users": {
            "cookie": {
                "name": "",
                "is_admin": False,
                "cards": [
                    "<cards._id>",
                ],
                "points": 0,
            },
        },
        "round": {
            "n": 0,
            "black": "<cards._id>",
        },
        "password": None,
    },
    "cards": {
        "_id": 0,
        "text": "",
        "pick": 1,
    }
}

# INFO REQUESTS


def user_rooms(user_cookie):
    # user's rooms
    return db.room.find(
        {"users": {user_cookie: {"$exists": True}}},
        {"_id": 1}
    )


def user_cards(room_id, user_cookie):
    # room's user's cards
    cards = db.room.find(
        {"_id": room_id},
        {"users": 1}
    )["users"][user_cookie]["cards"]
    return db.room.find(
        {"_id": {"$in": cards}},
    )


def current_black(room_id):
    # room's current black
    black = db.room.find(
        {"_id": room_id},
        {"round": 1}
    )["round"]["black"]
    return = db.room.find(
        {"_id": black},
    )


def user_points(room_id):
    # room's users' points
    users = db.room.find(
        {"_id": room_id},
        {"users": 1}
    )
    return [
        {u["name"]: u["points"]}
        for u in users
    ]

# ACTIONS

def create_room():
    pass


def use_card(room_id, user_cookie, card_id):
    pass


def choose_winner(room_id, card_token):
    pass

# PUSH


def you_are_caesar():
    pass


def card_used():
    pass


def new_black():
    pass


def card_uncover():
    pass


def drawn_cards():
    pass


def declare_winner():
    pass