from DatabaseController import Room

print("Scegli un nome per la tua stanza:\n")
room_name = input()
my_room = Room(room_name)

users = {}
temp = True

while temp:
    print("Scegli un nome utente:\n")
    user_name = input()
    users[user_name] = my_room.add_new_user(user_name)
    print("Ci sono altri utenti? (y/n):\n")
    inp = input()
    if inp == "n":
        temp = False

carta_nera = my_room.pick_random_black_card()

print("La carta nera pescata è: \n" + str(carta_nera))

cards_in_hand = {}

for name, u_id in users.items():
    pesca = my_room.pick_n_random_white_cards(7, u_id)[1]
    cards_in_hand[u_id] = pesca[0]
    carte = pesca
    print(str(name) + " ha pescato: \n" + str(carte))
