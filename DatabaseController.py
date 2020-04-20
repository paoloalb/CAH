import pymongo
import json
import random
from bson.objectid import ObjectId

class Room:

    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["cah"]
    cards_collection = mydb["cards"]
    room_collection = mydb["rooms"]

    def __init__(self, room_name, user_list):
    	self.room_info = {"room_name": room_name, "used_black_cards": [], "user_list": user_list}
    	room_document = self.room_collection.insert_one(self.room_info)
    	self.room_id = room_document.inserted_id

    def add_new_cards(self, input_card_list):  # Add new documents from a list
        with open(input_card_list, 'r') as f:
            card_data = json.load(f)

        for diz in card_data:
            x = self.cards_collection.insert_one(diz)
            print("New document inserted with ID: " + str(x.inserted_id))

    def erase_all_cards(self):  # Delete EVERYTHING in the "cards" collection
        success = self.cards_collection.delete_many({})
        return success

    def add_new_white_card(self, text):
        doc = {"text": text, "pick": 0}
        self.cards_collection.insert_one(doc)

    def add_new_black_card(self, text, pick):
        doc = {"text": text, "pick": pick}
        self.cards_collection.insert_one(doc)

    def pick_random_black_card(self):  # Returns text and pick value of a random black card
    	myquery = { "pick": { "$gt": 0 }, "_id": { "$nin": self.room_info["used_black_cards"]} }  # Query to select unused black cards
    	myresults = self.cards_collection.find(myquery)
    	result_card = myresults[random.randint(0, myresults.count()-1)] # Select random document
    	self.room_info["used_black_cards"].append(result_card["_id"]) # Add card to already used list
    	self.room_collection.update_one({"_id" : self.room_id}, { "$set": self.room_info})
    	return result_card["text"], result_card["pick"]

    def pick_random_white_card(self):  # Returns text of a random white card
    	myquery = { "pick": 0 }
    	myresults = self.cards_collection.find(myquery)
    	result_card = myresults[random.randint(0, myresults.count()-1)] # Select random document
    	return result_card["text"]
    	# Aggiungere in futuro il parametro utente, in modo da escludere carte già pescate.
