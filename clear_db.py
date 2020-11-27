import json

from pymongo import MongoClient

#
client = MongoClient("mongodb+srv://paoloa:123stella@mflix-3d6kd.mongodb.net/test")
db = client["cah"]
db["rooms"].delete_many({})
db["users"].delete_many({})
db["cards"].delete_many({})
db["cards_ita"].delete_many({})

with open("data/cards.json", "r") as f:
    cards = json.load(f)

db["cards"].insert_many(cards)

with open("data/cards_ita.json", "r") as f:
    cards = json.load(f)

db["cards_ita"].insert_many(cards)
