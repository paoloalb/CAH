from uuid import uuid4 as uuid

from flask import Blueprint, abort, make_response, redirect, request

cookies = Blueprint("cookies", __name__,)


def gen_cookie():
    return uuid().hex


@cookies.route("/biscottini")
def get_cookie():
    cookies = request.cookies
    ck = "id_card"
    url = request.path
    if url == "/biscottini":
        resp = make_response("OK", 200)
        if ck not in cookies:
            resp.set_cookie(ck, gen_cookie())
        return resp
    else:
        if ck in cookies:
            return str(cookies.get(ck))
        else:
            resp = redirect(url, 307)
            resp.set_cookie(ck, gen_cookie())
            abort(resp)
