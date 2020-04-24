import hashlib
import uuid


def hash_password(password, salt=None):
    if salt is None:
        salt = uuid.uuid4().bytes
    else:
        salt = salt
    password = password.encode("UTF-8")
    salted = password + salt
    hashed = hashlib.sha256(salted).hexdigest().encode("UTF-8")
    return hashed, salt
