import json
import random

import requests

url = "http://127.0.0.1:5000"


def check_match(value, check, trace=None):
    if type(check) is type:
        assert type(value) is check, [value, type(value), check, trace]
    elif callable(check):
        assert check(value) is True, [value, trace]
    else:
        assert type(value) is type(check), [value, type(value), check, type(check), trace]
    t = type(value)
    if hasattr(value, "__iter__") and t is type(check) and t not in [str, ]:
        if t is dict:
            present = sorted(list(value.keys()))
            expected = sorted(list(check.keys()))
            if "$$optionals$$" in check:
                present = [k for k in present if k not in check["$$optionals$$"]]
                expected = [k for k in expected if k not in check["$$optionals$$"] + ["$$optionals$$"]]
            assert present == expected, [present, expected, trace]
            if trace is None:
                trace = []
            for k, v in value.items():
                assert k in check, ["missing key {} in checks".format(k), trace]
                kc = k
                vc = check[k]
                t = trace + [k]
                check_match(k, kc, t)
                check_match(v, vc, t)
        elif any([t is i for i in [list, ]]):
            for v in value:
                check_match(v, check[0])
        else:
            raise NotImplementedError("checks for iterable type {}".format(t))


class Player:
    def __init__(self):
        self.session = requests.Session()

    def get_cookie(self):
        r = self.session.get(url + "/biscottini")
        assert r.status_code == 200
        assert r.text == "OK"
        cookies = requests.utils.dict_from_cookiejar(self.session.cookies)
        assert "id_card" in cookies
        assert len(cookies["id_card"]) > 0
        return cookies["id_card"]

    # ----- lobby_api tests -----

    def rooms(self):
        r = self.session.get(url + "/rooms")
        assert r.status_code == 200
        j = r.json()
        check_match(j, [{
            "_id": str,
            "name": str,
            "passworded": bool,
            "user_count_max": int,
            "user_count": int,
        }, ])
        return j

    def joined_rooms(self):
        r = self.session.get(url + "/joined_rooms")
        assert r.status_code == 200
        j = r.json()
        check_match(j, [{
            "_id": str,
            "name": str,
            "play_time": int,
            "passworded": bool,
            "user_count_max": int,
            "user_count": int,
            "round": int,
        }, ])
        return j

    def create_room(self, room_name, password=None, play_time=None, user_count_max=None, username=None):
        config = {"name": room_name}
        if password is not None:
            config["password"] = password
        if play_time is not None:
            config["play_time"] = play_time
        if user_count_max is not None:
            config["user_count_max"] = user_count_max
        if username is not None:
            config["username"] = username
        r = self.session.post(url + "/create_room", json=config)
        assert r.status_code == 200
        j = r.json()
        check_match(j, {"room_id": str, "public_id": str})
        return j["room_id"], j["public_id"]

    def join_room(self, room_id, username=None, password=None):
        config = {}
        if username is not None:
            config["username"] = username
        if password is not None:
            config["password"] = password
        r = self.session.get(url + "/join_room/" + room_id, json=config)
        assert r.status_code == 200
        j = r.json()
        check_match(j, {"public_id": str})
        return j["public_id"]

    def leave_room(self, room_id):
        r = self.session.get(url + "/leave_room/" + room_id)
        assert r.status_code == 200
        assert r.text == "OK"

    # ----- api tests -----

    def players(self, room_id):
        r = self.session.get(url + "/players/" + room_id)
        assert r.status_code == 200
        j = r.json()
        check_match(j, [{
            "public_id": str,
            "name": str,
            "points": int,
        }, ])
        return j

    def new_round(self, room_id):
        r = self.session.get(url + "/new_round/" + room_id)
        assert r.status_code == 200
        assert r.text == "OK"

    def hand(self, room_id):
        r = self.session.get(url + "/hand/" + room_id)
        assert r.status_code == 200
        j = r.json()
        check_match(j, [{
            "_id": str,
            "text": str,
            "pick": int,
            "$$optionals$$": ["pick"],
        }, ])
        return j

    def play_cards(self, room_id, cards):
        config = {"cards": cards}
        r = self.session.get(url + "/play_cards/" + room_id, json=config)
        assert r.status_code == 200
        assert r.text == "OK"

    def table(self, room_id):
        r = self.session.get(url + "/table/" + room_id)
        assert r.status_code == 200
        j = r.json()
        check_match(j, {
            "round": int,
            "time_left": float,
            "black": {
                "_id": str,
                "text": str,
                "pick": int,
                "$$optionals$$": ["pick"],
            },
            "caesar": str,
            "cards": [{
                "_id": str,
                "text": str,
                "pick": int,
                "$$optionals$$": ["pick"],
            }, ] if j["round_ended"] else int,
            "round_ended": bool,
            "winner": {
                "public_id": str,
                "cards": [{
                    "_id": str,
                    "text": str,
                    "pick": int,
                    "$$optionals$$": ["pick"],
                }, ],
            } if j["winner"] is not None else None,
        })
        return j

    def card_wins(self, room_id, card_id):
        r = self.session.get(url + "/card_wins/" + room_id + "/" + card_id)
        assert r.status_code == 200
        assert r.text == "OK"


# ----- AUTH TEST -----

# CREATE USER A
player_a = Player()
cookie_a = player_a.get_cookie()
print("a", "cookie:", cookie_a, sep="\t")
# CREATE USER B
player_b = Player()

# ----- LOBBY TEST ----

# print("a", "rooms:", json.dumps(info, indent="\t"), sep="\t")-
# A CREATE ROOM
username_a = "test_player_a"
room_name = "test_room"
room_password = "test_password"
play_time = 5
user_count_max = 4
room, id_a = player_a.create_room(room_name, password=room_password, play_time=play_time, user_count_max=user_count_max, username=username_a)
print("a", "create_room:", room, "username:", username_a, sep="\t")
# A ROOMS INFO
info = player_a.rooms()
# A JOINED ROOMS INFO
info = player_a.joined_rooms()
# print("a", "joined_rooms:", json.dumps(info, indent="\t"), sep="\t")
assert len(info) == 1
assert info[0]["_id"] == room
assert info[0]["name"] == room_name
assert info[0]["play_time"] == play_time
assert info[0]["passworded"] is True
assert info[0]["user_count_max"] == user_count_max
assert info[0]["user_count"] == 1
assert info[0]["round"] == 0
# B JOIN ROOM
username_b = "test_player_b"
id_b = player_b.join_room(room, username=username_b, password=room_password)
print("b", "join_room:", room, "username:", username_b, sep="\t")
# B JOINED ROOMS INFO
info = player_b.joined_rooms()
# print("b", "joined_rooms:", json.dumps(info, indent="\t"), sep="\t")
assert len(info) == 1
assert info[0]["_id"] == room
assert info[0]["name"] == room_name
assert info[0]["play_time"] == play_time
assert info[0]["passworded"] is True
assert info[0]["user_count_max"] == user_count_max
assert info[0]["user_count"] == 2
assert info[0]["round"] == 0

# ----- PLAY TEST -----

players_map = {
    id_a: player_a,
    id_b: player_b,
}
players_points = {
    id_a: 0,
    id_b: 0,
}
round = 0
while round < 8:
    round += 1
    print("round", round, sep="\t")
    # A PLAYERS
    players = player_a.players(room)
    for player in players:
        assert player["public_id"] in [id_a, id_b]
        assert player["name"] in [username_a, username_b]
        assert player["points"] == players_points[player["public_id"]]
    # A NEW ROUND
    player_a.new_round(room)
    # A TABLE
    table = player_a.table(room)
    assert table["caesar"] in players_map
    caesar = players_map[table["caesar"]]
    assert table["round"] == round
    assert table["time_left"] > play_time - 1
    assert table["round_ended"] is False
    assert table["cards"] == 0
    assert table["winner"] is None
    assert table["black"]["pick"] > 0
    hands = {}
    delt_cards = []
    for id, player in players_map.items():
        # PLAYER HAND
        hands[id] = player.hand(room)
        delt_cards += [card["_id"] for card in hands[id]]
    assert len(set(delt_cards)) == len(delt_cards)
    played_cards = []
    for id, player in players_map.items():
        if id != table["caesar"]:
            cards = random.sample(hands[id], k=table["black"]["pick"])
            played_cards += cards
            # PLAYER PLAY CARDS
            player.play_cards(room, [card["_id"] for card in cards])
            print(id, "play_cards", sep="\t")
    # CAESAR TABLE
    table = caesar.table(room)
    assert table["round"] == round
    assert table["black"]["pick"] > 0
    assert len(table["cards"]) == table["black"]["pick"] * (len(players_map) - 1)
    cards = table["cards"]
    assert table["round_ended"] is True
    assert table["winner"] is None
    winner_card = random.sample(table["cards"], k=1)[0]["_id"]
    # CAESAR CARD WINS
    caesar.card_wins(room, winner_card)
    # CAESAR TABLE
    table = caesar.table(room)
    assert table["round"] == round
    assert table["black"]["pick"] > 0
    assert len(table["cards"]) == table["black"]["pick"] * (len(players_map) - 1)
    cards = table["cards"]
    assert table["round_ended"] is True
    assert table["winner"]["public_id"] is not table["caesar"]
    assert winner_card in [card["_id"] for card in table["winner"]["cards"]]
    players_points[table["winner"]["public_id"]] += 1
    print(table["winner"]["public_id"], "wins", sep="\t")

# ----- LOBBY TEST -----

# A LEAVE
player_a.leave_room(room)
print("a", "leave:", room, sep="\t")
# A LIST ROOMS
info = player_a.joined_rooms()
print("a", "rooms:", json.dumps(info, indent="\t"), sep="\t")
assert len(info) == 0
