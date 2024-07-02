import secrets
import base64
import sys


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


def basic_auth(username, password):
    # base64 encodes the username and password
    return f"Basic {base64.b64encode(f'{username}:{password}'.encode('utf-8')).decode('utf-8')}"
