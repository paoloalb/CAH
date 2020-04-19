import pymongo
import json
import random

class CardDealer:

    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["cah"]
    mycol = mydb["cards"]

    #   def __init__(self):

    def add_new_cards(self, input_card_list):  # Add new documents from a list
        with open(input_card_list, 'r') as f:
            card_data = json.load(f)

        for diz in card_data:
            x = self.mycol.insert_one(diz)
            print("New document inserted with ID: " + str(x.inserted_id))

    def erase_all_cards(self):  # Delete EVERYTHING in the "cards" collection
        success = self.mycol.delete_many({})
        return success

    def add_new_white_card(self, text):
        doc = {"text": text, "pick": 0}
        self.mycol.insert_one(doc)

    def add_new_black_card(self, text, pick):
        doc = {"text": text, "pick": pick}
        self.mycol.insert_one(doc)

    def pick_random_black_card(self):  # Returns text and pick value of a random black card
    	myquery = { "pick": { "$gt": 0 } }
    	myresults = self.mycol.find(myquery)
    	result_card = myresults[random.randint(0, myresults.count()-1)] # Select random document
    	return result_card["text"], result_card["pick"]

    def pick_random_white_card(self):  # Returns text of a random white card
    	myquery = { "pick": 0 }
    	myresults = self.mycol.find(myquery)
    	result_card = myresults[random.randint(0, myresults.count()-1)] # Select random document
    	return result_card["text"]
    	# Aggiungere in futuro il parametro utente, in modo da escludere carte già pescate.
