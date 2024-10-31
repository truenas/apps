import hashlib
import secrets
import bcrypt
import sys
import re

from . import security


class TemplateException(Exception):
    pass


def throw_error(message):
    # When throwing a known error, hide the traceback
    # This is because the error is also shown in the UI
    # and having a traceback makes it hard for user to read
    sys.tracebacklimit = 0
    raise TemplateException(message)


def secure_string(length):
    return secrets.token_urlsafe(length)


def basic_auth_header(username, password):
    return f"Basic {security.basic_auth(username, password)}"


def bcrypt_hash(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def match_regex(value, regex):
    if not re.match(regex, value):
        return False
    return True


def must_match_regex(value, regex):
    if not match_regex(value, regex):
        throw_error(f"Expected [{value}] to match [{regex}]")
    return value


def merge_dicts(*dicts):
    merged_dict = {}
    for dictionary in dicts:
        merged_dict.update(dictionary)
    return merged_dict


# Basic validation for a path (Expand later)
def valid_path(path=""):
    if not path.startswith("/"):
        throw_error(f"Expected path [{path}] to start with /")

    # There is no reason to allow / as a path, either on host or in a container
    if path == "/":
        throw_error(f"Expected path [{path}] to not be /")

    return path


def camel_case(string):
    return string.title()


def is_boolean(string):
    return string.lower() in ["true", "false"]


def is_number(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


def get_image(images={}, name=""):
    if not images:
        throw_error("Expected [images] to be set")
    if name not in images:
        throw_error(f"Expected [images.{name}] to be set")
    if not images[name].get("repository") or not images[name].get("tag"):
        throw_error(f"Expected [images.{name}.repository] and [images.{name}.tag] to be set")

    return f"{images[name]['repository']}:{images[name]['tag']}"


def hash_data(data=""):
    if not data:
        throw_error("Expected [data] to be set")
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def get_image_with_hashed_data(images={}, name="", data=""):
    return f"ix-{get_image(images, name)}-{hash_data(data)}"


def copy_dict(dict):
    return dict.copy()


def escape_dollar(text: str) -> str:
    return text.replace("$", "$$")


def auto_cast(value):
    try:
        return int(value)
    except ValueError:
        pass

    try:
        return float(value)
    except ValueError:
        pass

    if value.lower() in ["true", "false"]:
        return value.lower() == "true"

    return value
