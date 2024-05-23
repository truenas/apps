import secrets
import yaml
import sys


class TemplateException(Exception):
    pass


def throw_error(message):
    # When throwing a known error, hide the traceback
    # This is because the error is also shown in the UI
    # and having a traceback makes it hard for user to read
    sys.tracebacklimit = 0
    raise TemplateException(message)


def get_yaml_opts():
    return {
        "default_flow_style": False,
        "sort_keys": False,
        "indent": 2,
    }


def to_yaml(data):
    return yaml.dump(data, **get_yaml_opts())


def secure_string(length):
    return secrets.token_urlsafe(length)
