from base64 import b64encode


def get_caps(add=[], drop=[]):
    result = {"drop": drop or ["ALL"]}
    if add:
        result["add"] = add
    return result


def get_sec_opts(add=[], remove=[]):
    result = ["no-new-privileges"]
    for opt in add:
        if opt not in result:
            result.append(opt)
    for opt in remove:
        if opt in result:
            result.remove(opt)
    return result


def htpasswd(username, password):
    return b64encode(f"{username}:{password}".encode("utf-8")).decode("utf-8")
