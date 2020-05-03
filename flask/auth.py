import hashlib
from uuid import uuid4 as uuid

from flask import Blueprint, abort, make_response, redirect, request

auth = Blueprint("auth", __name__,)


def gen_cookie():
    return uuid().hex


@auth.route("/biscottini")
def get_cookie():
    cookies = request.cookies
    ck = "id_card"
    if request.path == "/biscottini":
        resp = make_response("OK", 200)
        if ck not in cookies:
            resp.set_cookie(ck, gen_cookie())
        return resp
    else:
        if ck in cookies:
            return str(cookies.get(ck))
        else:
            resp = redirect(request.path, 307)
            resp.set_cookie(ck, gen_cookie())
            abort(resp)


def hash_password(password, salt=None):
    if salt is None:
        salt = uuid().bytes
    else:
        salt = salt
    password = password.encode("UTF-8")
    salted = password + salt
    hashed = hashlib.sha256(salted).hexdigest().encode("UTF-8")
    return hashed, salt
