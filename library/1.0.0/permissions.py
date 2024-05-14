from . import utils
import pathlib
import re
import os

RE_ID = re.compile(r"^[0-9]+$")
RE_MODE = re.compile(r"^(0o)?([0-7]{3})$")


def chown(path, uid, gid):
    if not pathlib.Path(path).exists():
        utils.throw_error(f"Path [{path}] does not exist")

    if not RE_ID.match(uid):
        utils.throw_error(f"User ID must be a number, but got [{uid}]")
    if not RE_ID.match(gid):
        utils.throw_error(f"Group ID must be a number, but got [{gid}]")

    os.chown(path, int(uid), int(gid))
    return ""


def chmod(path, mode):
    if not pathlib.Path(path).exists():
        utils.throw_error(f"Path [{path}] does not exist")

    if not RE_MODE.match(mode):
        utils.throw_error(
            f"Mode must be in octal format, but got [{mode}]. Example: 0o755 or 755"
        )

    os.chmod(path, int(mode, 8))
    return ""
