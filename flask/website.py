from flask import Blueprint, render_template

website = Blueprint('website', __name__, )


@website.route('/')
def root():
    return render_template('index.html',
                           rooms=[
                               {"name": "room1"},
                               {"name": "room2"},
                               {"name": "room3"},
                               {"name": "room4"},
                               {"name": "room5"},
                               {"name": "room6"},
                           ],
                           player_rooms=[
                               {
                                   "name": "room1",
                                   "players": [
                                       {"name": "player1"},
                                       {"name": "player2"},
                                       {"name": "player3"},
                                   ],
                               },
                               {
                                   "name": "room2",
                                   "players": [
                                       {"name": "player4"},
                                       {"name": "player5"},
                                       {"name": "player6"},
                                   ],
                               },
                           ]
                           )


@website.route('/UserPage')
def UserPage():
    return render_template('UserPage.html')
