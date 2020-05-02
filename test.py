import json

import requests

url = "http://127.0.0.1:5000"


class User:
    def __init__(self):
        self.session = requests.Session()

    def get_cookie(self):
        r = self.session.get(url + "/biscottini")
        assert r.status_code == 200 and r.text == "OK"
        cookies = requests.utils.dict_from_cookiejar(self.session.cookies)
        assert "id_card" in cookies
        assert len(cookies["id_card"]) > 0
        return cookies["id_card"]

    def create_room(self, room_name):
        r = self.session.post(url + "/new_room", json={"name": "test_room"})
        assert r.status_code == 200
        j = r.json()
        assert "room_id" in j
        return j["room_id"]

    def join_room(self, room_id, username):
        r = self.session.get(url + "/join_room/" + room_id + "/" + username)
        assert r.status_code == 200
        assert r.text == "OK"

    def leave_room(self, room_id):
        r = self.session.get(url + "/leave_room/" + room_id)
        assert r.status_code == 200
        assert r.text == "OK"

    def my_rooms(self):
        r = self.session.get(url + "/my_rooms_info")
        assert r.status_code == 200
        j = r.json()
        assert "rooms" in j
        assert type(j["rooms"]) is list
        return j["rooms"]

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

# CREATE USER A
cookie_a = player_a.get_cookie()
print("a", "cookie:", cookie_a, sep="\t")
# CREATE USER B
cookie_b = player_b.get_cookie()
print("b", "cookie:", cookie_b, sep="\t")
# A CREATE ROOM
room = player_a.create_room("test_room")
print("a", "room:", room, sep="\t")
# A JOIN ROOM
username_a = "test_player_a"
player_a.join_room(room, username_a)
print("a", "joined:", room, "username:", username_a, sep="\t")
# B JOIN ROOM
username_b = "test_player_b"
player_b.join_room(room, username_b)
print("b", "joined:", room, "username:", username_b, sep="\t")
# A LIST ROOMS
rooms_a = player_a.my_rooms()
print("a", "rooms:", json.dumps(rooms_a, indent="\t"), sep="\t")
# B LIST ROOMS
rooms_b = player_b.my_rooms()
print("b", "rooms:", json.dumps(rooms_b, indent="\t"), sep="\t")
# A PICK CARDS
cards_a = player_a.pick_white_cards(5, room)
print("a", "cards:",  json.dumps(cards_a, indent="\t"), sep="\t")
# B PICK CARDS
cards_b = player_b.pick_white_cards(5, room)
print("b", "cards:",  json.dumps(cards_b, indent="\t"), sep="\t")
# A PICK BLACK
black = player_a.pick_black(room)
pick = black["pick"]
print("a", "black:", black["text"], "pick:", pick, sep="\t")
# A PLAY CARDS
play_ids_a = list(range(pick))
player_a.play_cards(room, play_ids_a)
print("a", "play:", [cards_a[i]["text"] for i in play_ids_a], sep="\t")
# B PLAY CARDS
play_ids_b = list(range(pick))
player_b.play_cards(room, play_ids_b)
print("a", "play:", [cards_a[i]["text"] for i in play_ids_b], sep="\t")
# A WINS
player_a.user_wins(room)
print("a", "win", sep="\t")
# B LEAVE
player_a.leave_room(room)
print("a", "leave:", room, sep="\t")
# B LIST ROOMS
rooms_b = player_a.my_rooms()
print("a", "rooms:", json.dumps(rooms_b, indent="\t"), sep="\t")
