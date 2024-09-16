from base64 import b64encode

from . import utils


def get_caps(add=None, drop=None):
    add = add or []
    drop = drop or ["ALL"]
    result = {"drop": drop}
    if add:
        result["add"] = add
    return result


def get_sec_opts(add=None, remove=None):
    add = add or []
    remove = remove or []
    result = ["no-new-privileges"]
    for opt in add:
        if opt not in result:
            result.append(opt)
    for opt in remove:
        if opt in result:
            result.remove(opt)
    return result


def htpasswd(username, password):
    hashed = utils.bcrypt_hash(password)
    return username + ":" + hashed


def basic_auth(username, password):
    return b64encode(f"{username}:{password}".encode("utf-8")).decode("utf-8")
