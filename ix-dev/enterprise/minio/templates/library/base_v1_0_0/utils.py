import secrets
import sys

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
    return f"Basic {security.htpasswd(username, password)}"


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
