from pymongo import MongoClient

client = MongoClient("mongodb+srv://paoloa:123stella@mflix-3d6kd.mongodb.net/test")
# client = MongoClient("mongodb://localhost:27017/")
db = client["cah"]
cards_collection = db["cards_ita"]
rooms_collection = db["rooms"]
users_collection = db["users"]

# DB SCHEMA
db = {
    "room": [{
        "_id": 0,
        "name": "",
        "play_time": 45,
        "passworded": False,
        "password": None,
        "user_count_max": 5,
        "states": [{
            "user": "<users._id>",
            "public_id": "<uuid>",
            "name": "",
            "cards_in_hand": ["<cards._id>", ],
            "cards_on_table": ["<cards._id>", ],
            "points": 0,
        }, ],
        "admins": ["<users._id>", ],
        "round": 0,
        "round_start_time": None,
        "caesar": "<states.public_id>",
        "black": "<card>",
        "round_ended": None,
        "winner": {
            "public_id": "<states.public_id>",
            "cards": ["<card>", ],
        },
        "used_white_cards": ["<cards._id>", ],
        "used_black_cards": ["<cards._id>", ],
    }, ],

    "users": [{
        "rooms": ["<rooms._id>", ],
    }, ],

    "cards": [{
        "_id": 0,
        "text": "",
        "pick": 0,
    }, ],
}
