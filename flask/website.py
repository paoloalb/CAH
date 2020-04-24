from flask import Blueprint, render_template

website = Blueprint('website', __name__, )


@website.route('/')
def root():
    return render_template('index.html',
    rooms=[
        {"_id": 1, "name": "room1"},
        {"_id": 2, "name": "room2"},
        {"_id": 3, "name": "room3"},
        {"_id": 4, "name": "room4"},
        {"_id": 5, "name": "room5"},
        {"_id": 6, "name": "room6"},
    ],
    player_rooms=[
        {
            "_id": 1,
            "name": "room1",
            "players": [
                {"name": "player1"},
                {"name": "player2"},
                {"name": "player3"},
            ],
        },
        {
            "_id": 2,
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
