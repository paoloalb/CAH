import json

import requests

url = "http://127.0.0.1:5000"
N_OF_CARDS = 5

class User:
    def __init__(self):
        self.session = requests.Session()

    def get_cookie(self):
        r = self.session.get(url + "/biscottini")
        assert r.status_code == 200 and r.text == "OK"
        cookies = requests.utils.dict_from_cookiejar(self.session.cookies)
        assert "id_card" in cookies and len(cookies["id_card"]) > 0
        return cookies["id_card"]

    def create_room(self, room_name):
        room_id = self.session.post(url + "/new_room", json={"name": "test_room"}).json()["room_id"]
        assert type(room_id) is str and len(room_id) > 0
        return room_id

    def join_room(self, room_id, username):
        r = self.session.get(url + "/join_room/" + room_id + "/" + username)
        assert r.status_code == 200 and r.text == "OK"

    def my_rooms(self):
        rooms = self.session.get(url + "/my_rooms").json()
        assert "rooms" in rooms and type(rooms["rooms"]) is list
        return rooms

    def pick_white_cards(self, n, room_id):
        card_list = self.session.get(url + "/randomWhiteCards/" + room_id + "/" + str(n)).json()
        return card_list

    def pick_black(self, room_id):
        black_card = self.session.get(url + "/randomBlackCard/" + room_id).json()
        return black_card

    def play_cards(self, room_id, list_of_ids):
        self.session.get(url + "/play_cards/" + room_id, json={"list": list_of_ids})

    def user_wins(self, room_id):
        self.session.get(url + "/user_wins/" + str(room_id))

    def current_black(self, room_id):
        black_card = self.session.get(url + "/current_black/" + room_id).json()
        return black_card

    def current_white(self, room_id):
        white_cards = self.session.get(url + "/current_white/" + room_id).json()
        return white_cards

    def user_list(self, room_id):
        users = self.session.get(url + "/user_list/" + room_id).json()
        return users

player_a = User()
player_b = User()

cookie_a = player_a.get_cookie()
print("a", "cookie:", cookie_a, sep="\t")

cookie_b = player_b.get_cookie()
print("b", "cookie:", cookie_b, sep="\t")

room = player_a.create_room("test_room")
print("a", "room:", room, sep="\t")

username_a = "test_player_a"
player_a.join_room(room, username_a)
print("a", "joined:", room, "username:", username_a, sep="\t")

username_b = "test_player_b"
player_b.join_room(room, username_b)
print("b", "joined:", room, "username:", username_b, sep="\t")

rooms_a = player_a.my_rooms()
print("a", "rooms:", json.dumps(rooms_a, indent="\t"), sep="\t")

rooms_b = player_b.my_rooms()
print("b", "rooms:", json.dumps(rooms_b, indent="\t"), sep="\t")

cards_a = player_a.pick_white_cards(N_OF_CARDS, room)
print("\na picked these cards: \n",  json.dumps(cards_a, indent="\t"))

cards_b = player_b.pick_white_cards(N_OF_CARDS, room)
print("\nb picked these cards: \n",  json.dumps(cards_b, indent="\t"))

black_card = player_a.pick_black(room)
print("\nblack card was picked:\n" + black_card["text"] + "\nPick " + str(black_card["pick"]))

input_string = input("\nInserisci la posizione delle carte da giocare per il player a separate da uno spazio (x es: 0 2 3):\n")
list_of_ids = [c["_id"] for i, c in enumerate(cards_a) if i in [int(u) for u in input_string.split()]]
player_a.play_cards(room, list_of_ids)
print("\nplayer_a ha giocato le seguenti carte:\n" + str([c["text"] for i, c in enumerate(cards_a) if i in [int(u) for u in input_string.split()]]))

input_string = input("Inserisci la posizione delle carte da giocare per il player b separate da uno spazio (x es: 0 2 3):\n")
list_of_ids = [c["_id"] for i, c in enumerate(cards_b) if i in [int(u) for u in input_string.split()]]
player_b.play_cards(room, list_of_ids)
print("\nplayer_b ha giocato le seguenti carte:\n" + str([c["text"] for i, c in enumerate(cards_b) if i in [int(u) for u in input_string.split()]]))


print("select a winner (a/b):\n")
winner = input()
if winner == "a":
    player_a.user_wins(room)
    print("player a was granted 1 point!")
elif winner == "b":
    player_b.user_wins(room)
    print("player b was granted 1 point!")
