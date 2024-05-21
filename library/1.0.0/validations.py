from . import utils


def validate_path(path):
    if not path:
        utils.throw_error("Path must be set")

    if not path.startswith("/"):
        utils.throw_error(f"Path [{path}] must start with [/]")

    return path
