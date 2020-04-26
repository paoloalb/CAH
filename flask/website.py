from api import *
from flask import Blueprint, render_template

website = Blueprint('website', __name__, )


@website.route('/')
def root():
    return render_template('index.html', rooms=rooms(), player_rooms=user_rooms())


@website.route('/UserPage')
def UserPage():
    card = random_black_card()
    print(type(card))
    return render_template('UserPage.html', whiteCards=random_white_cards_test(3), blackCard=card)
