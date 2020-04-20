import pymongo
import json
import random
from bson.objectid import ObjectId

class Room:

    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["cah"]
    cards_collection = mydb["cards"]
    room_collection = mydb["rooms"]
    users_collection = mydb["users"]

    def __init__(self, room_name):
        room_document = {"room_name": room_name, "used_black_cards": [], "users_list": []}
        insert_room = self.room_collection.insert_one(room_document)
        self.room_id = insert_room.inserted_id

    def add_new_user(self, user_name):
        user_doc = {"name": user_name, "points": 0, "cards_in_hand": [], "used_white_cards": []}
        insert_user = self.users_collection.insert_one(user_doc)
        self.room_collection.update_one({"_id" : self.room_id}, { "$push": { "users_list": insert_user.inserted_id} })
        return insert_user.inserted_id

    def user_wins(self, winning_user_id):
        self.users_collection.update_one({"_id" : winning_user_id}, { "$inc": { "points": 1 } })


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
        list_of_used_cards = self.room_collection.find_one({"_id": self.room_id})["used_black_cards"]  # Find used black cards
        myquery = { "pick": { "$gt": 0 }, "_id": { "$nin": list_of_used_cards} }  # Query to select all unused black cards
        myresults = self.cards_collection.find(myquery)
        result_card = myresults[random.randint(0, myresults.count()-1)] # Select random document
        # Add card to already used list:
        self.room_collection.update_one({"_id" : self.room_id}, { "$push": { "used_black_cards": result_card["_id"]} })
        return result_card["text"], result_card["pick"]

    def pick_n_random_white_cards(self, n, user_id):  # Takes the user who is picking the card as an argument
        myquery = { "pick": 0 }
        myresults = list(self.cards_collection.find(myquery)) 
        result_cards = random.sample(myresults, n)
        for rc in result_cards:  # Updates the list of cards already used by this person:
            self.users_collection.update_one({"_id" : user_id}, { "$push": { "used_white_cards": rc["_id"]} })
            self.users_collection.update_one({"_id" : user_id}, { "$push": { "cards_in_hand": rc["_id"]} })
        return [rc["text"]  for rc in result_cards]