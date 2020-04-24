# DB SCHEMA
db = {
    "room": [
        {
            "_id": 0,
            "room_name": "",
            "black": "<cards._id>", # ID della carta che si trova sul tavolo
            "caesar": "<user._id>",
            "users": [
                "<user._id>",
            ],
            "used_cards": [
                "<cards._id>",
            ],
            "round": 0,
            "admins": [
                "<user._id>",
            ],
            "password": None,
        },
    ]

    "users": [
        {
            "_id": 0,
            "cookie": "",
            "name": "",
            "admin": False,
            "room": "<room._id>",
            "cards_on_hand": [
                "<cards._id>",
            ],
            "cards_on_table":[
                "<cards._id>",
            ],
            "points": 0,
        },
    ],

    "cards": [
        {
            "_id": 0,
            "text": "",
            "pick": 1,
        },
    ],
}

# INFO REQUESTS


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
