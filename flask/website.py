from flask import Blueprint, render_template

website = Blueprint('website', __name__,)


@website.route('/')
def root():
    return render_template('index.html')
