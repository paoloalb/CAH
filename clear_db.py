from pymongo import MongoClient

client = MongoClient("mongodb+srv://paoloa:123stella@mflix-3d6kd.mongodb.net/test")
db = client["cah"]
db["rooms"].delete_many({})
db["users"].delete_many({})
