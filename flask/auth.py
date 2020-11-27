import hashlib
from uuid import uuid4 as uuid

from bson.objectid import ObjectId
from db import users_collection
from flask import Blueprint, abort, make_response, redirect, request

auth = Blueprint("auth", __name__,)


def gen_user():
    return {
        "rooms": [],
    }


def gen_cookie():
    user = gen_user()
    inserted = users_collection.insert_one(user).inserted_id
    return str(inserted)


@auth.route("/biscottini")
def get_user():
    cookie_key = "id_card"
    if cookie_key in request.cookies:
        # if cookie alredy set get it
        cookie = request.cookies[cookie_key]
    else:
        # if no cookie create one
        cookie = gen_cookie()
        if request.path == "/biscottini":
            # respond ok to cookie request
            resp = make_response("OK", 200)
        else:
            # redirect request to set cookie
            resp = redirect(request.path, 307)
        # set cookie in response
        resp.set_cookie(cookie_key, cookie)
        abort(resp)
    # get user matching cookie
    user = users_collection.find_one({
        "_id": ObjectId(cookie),
    })
    if user is None:
        # if cookie doesn't match any user
        # redirect request to delete cookie
        resp = redirect(request.path, 307)
        resp.delete_cookie(cookie_key)
        abort(resp)
    return user


def hash_password(password, salt=None):
    if salt is None:
        salt = uuid().bytes
    else:
        salt = salt
    password = password.encode("UTF-8")
    salted = password + salt
    hashed = hashlib.sha256(salted).hexdigest().encode("UTF-8")
    return hashed, salt
