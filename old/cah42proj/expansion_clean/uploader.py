import pymongo
import json
import random
from bson.objectid import ObjectId


class DatabaseController():
    connection_string = #"mongodb://localhost:27017/"
    myclient = pymongo.MongoClient(connection_string)
    mydb = myclient["cah"]
    cards_collection = mydb["cards"]


    def add_new_card(self, text, pick):
        doc = {"text": text, "pick": pick}
        self.cards_collection.insert_one(doc)

dbc = DatabaseController()

FILENAME = "1_clean.txt"
frase = ""

with open(FILENAME) as f:
    for l in f:
        if not l.strip(): # se c'è un  acapo
            print(frase.replace('\n', ' '))
            pick_value = input()
            if pick_value != -1 and pick_value.isdigit():
                dbc.add_new_card(frase.replace('\n', ' '), pick_value)
            frase = ""
        else:
            frase+=l


        #in = input()
