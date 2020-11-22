from pymongo import MongoClient

client = MongoClient("mongodb+srv://paoloa:123stella@mflix-3d6kd.mongodb.net/test")
# client = MongoClient("mongodb://localhost:27017/")
db = client["cah"]
cards_collection = db["card_ita"]
rooms_collection = db["rooms"]
users_collection = db["user"]

# DB SCHEMA
db = {
    "room": [
        {
            "_id": 0,
            "name": "",
            "users": [
                "<user._id>",
            ],
            "admins": [
                "<user._id>",
            ],
            "round": 0,
            "black": "<cards._id>",
            "caesar": "<user._id>",
            "used_cards": [
                "<cards._id>",
            ],
            "user_count": 0,
            "user_count_max": 5,
            "password": None,
        },
    ],

    "user": [
        {
            "_id": 0,
            "cookie": "",
            "name": "",
            "room": "<room._id>",
            "cards_in_hand": [
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
