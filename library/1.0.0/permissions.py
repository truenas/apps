from . import utils
import re


RE_ID = re.compile(r"^[0-9]+$")
RE_MODE = re.compile(r"^(0o)?([0-7]{3})$")


def validate_id(id):
    if not RE_ID.match(str(id)):
        utils.throw_error(f"User/Group ID must be a number, but got [{id}]")


def validate_mode(mode):
    if not RE_MODE.match(mode):
        utils.throw_error(
            f"Mode must be in octal format, but got [{mode}]. Example: 0o755 or 755"
        )
