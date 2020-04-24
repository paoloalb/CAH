import pymongo
import json
import random
from bson.objectid import ObjectId


class DatabaseController():
    connection_string = "mongodb://localhost:27017/"
    myclient = pymongo.MongoClient(connection_string)
    mydb = myclient["cah"]
    cards_collection = mydb["cards"]
    rooms_collection = mydb["rooms"]
    users_collection = mydb["users"]

    def create_room(self, room_name, max_players):
        room_document = {"room_name": room_name, "black": None, "caesar": None,
        "users": [], "used_cards": [], "round": 0, "admins": [],
        "password": None, "max_n_of_players": max_players
        }
        insert_room = self.rooms_collection.insert_one(room_document)
        room_id = insert_room.inserted_id
        return str(room_id)

    def add_new_user(self, username, cookie, room_id):
        my_room = self.rooms_collection.find_one({"_id": ObjectId(room_id)})

        if len(my_room["users"]) >= my_room["max_n_of_players"]:  # Check if room is full
            raise Exception("The room is full! User was not added")

        res = self.users_collection.find_one({"cookie": cookie, "room": ObjectId(room_id)})
        if res is not None:
            raise Exception("L'utente risulta essere già registrato in questa stanza con questo cookie!")

        user_doc = {"cookie": cookie, "name": username, "admin": False, "room": ObjectId(room_id),
        "cards_in_hand": [], "cards_on_table": [], "points": 0}
        insert_user = self.users_collection.insert_one(user_doc)
        self.rooms_collection.update_one({"_id": ObjectId(room_id)}, {"$push": {"users": insert_user.inserted_id}})
        return str(insert_user.inserted_id)  # Returns the ID of the user as a string

    def find_rooms_from_cookie(self, user_cookie):  # given the cookie, returns all about his rooms
        myusers = list(self.users_collection.find({"cookie": user_cookie}, {"_id": 1}))
        found_rooms = [self.rooms_collection.find_one({"users": {"$elemMatch": {"$eq": u["_id"]}}}) for u in myusers]
        return found_rooms

    def basic_room_info(self):  # basic info about ALL rooms in the database
        all_rooms = list(self.rooms_collection.find({}, {"room_name": 1, "password": 1,
        "max_n_of_players": 1, "round": 1}))
        return all_rooms  # Returns list of basic info

    def user_info(self, cookie, room_id):  # given cookie and room id, return all info about user
        my_user = self.users_collection.find_one({"cookie": {"$eq": cookie}, "room": ObjectId(room_id)})
        return my_user

    def user_wins(self, winning_user_id):  # Cambiare! dare vittoria in base al card id
        my_user = self.users_collection.find_one({"_id": ObjectId(winning_user_id)})
        if my_user is None:  # Make sure that the user exists
            raise Exception('The provided user ID was not found in the database')
        self.users_collection.update_one({"_id": ObjectId(winning_user_id)}, {"$inc": {"points": 1}})

    def add_new_cards_to_db(self, input_card_list):  # Add new documents from a list
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

    def pick_random_black_card(self, room_id):  # Returns text and pick value of a random black card
        list_of_used_cards = self.rooms_collection.find_one({"_id": ObjectId(room_id)})["used_cards"]  # Find used black cards
        myquery = {"pick": {"$gt": 0}, "_id": {"$nin": list_of_used_cards}}  # Query to select all unused black cards
        myresults = self.cards_collection.find(myquery)
        result_card = myresults[random.randint(0, myresults.count()-1)]  # Select random document
        # Add card to already used list:
        self.rooms_collection.update_one({"_id": ObjectId(room_id)}, {"$push": {"used_cards": result_card["_id"]}, "$set": { "black":  result_card["_id"]} })
        return result_card["text"], result_card["pick"]

    def current_black(self, room_id):  # Takes room id as a string
        black = self.rooms_collection.find_one({"_id": ObjectId(room_id)}, {"black": 1})["black"]
        return str(black)  # returns ID of current black card as a string

    def pick_n_random_white_cards(self, n, user_id):  # Takes the user who is picking the card (as an ObjectID)
        my_user = self.users_collection.find_one({"_id": ObjectId(user_id)})
        if my_user is None:  # Make sure that the user exists
            raise Exception('The provided user ID was not found in the database')
        my_room_id = self.users_collection.find_one({"_id": ObjectId(user_id)})["room"]
        list_of_used_cards = self.rooms_collection.find_one({"_id": my_room_id})["used_cards"]  # Find used white cards
        myquery = {"pick": 0, "_id": {"$nin": list_of_used_cards}}
        myresults = list(self.cards_collection.find(myquery))
        if len(myresults) < n:
            raise Exception('Not enough new cards for this user')

        result_cards = random.sample(myresults, n)
        for rc in result_cards:  # Updates the list of cards already used by this person:
            self.rooms_collection.update_one({"_id": my_room_id}, {"$push": {"used_cards": rc["_id"]}})
            self.users_collection.update_one({"_id": ObjectId(user_id)}, {"$push": {"cards_in_hand": rc["_id"]}})
        return [rc["_id"] for rc in result_cards], [rc["text"] for rc in result_cards]

    def user_plays_cards(self, user_id, list_of_card_ids, room_id):
        my_user = self.rooms_collection.find_one({"users": ObjectId(user_id)})  # Controllare e debuggare bene!
        if my_user is None:  # Make sure that the user exists
            raise Exception('The provided user ID was not found in the room')
        for card in list_of_card_ids:
            my_card = self.users_collection.find_one({"_id": ObjectId(user_id), "cards_in_hand": ObjectId(card)})
            if my_card is None:  # Make sure that the card is in the hand of the user
                raise Exception('The provided card IDs were not found in the user\'s hand')

        for card in list_of_card_ids:
            self.rooms_collection.update_one({"_id":  ObjectId(room_id)}, {"$push": {"used_cards": ObjectId(card)}})
            self.users_collection.update_one({"_id": ObjectId(user_id)}, {"$pull": {"cards_in_hand": ObjectId(card)}})
            self.users_collection.update_one({"_id": ObjectId(user_id)}, {"$push": {"cards_on_table": ObjectId(card)}})
