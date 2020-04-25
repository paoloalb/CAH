from api import *
from flask import Blueprint, render_template

website = Blueprint('website', __name__, )


@website.route('/')
def root():
    return render_template('index.html', rooms=rooms(), player_rooms=user_rooms())


@website.route('/UserPage')
def UserPage():
    return render_template('UserPage.html', whiteCards=random_white_cards(3), blackCard=random_black_card())
