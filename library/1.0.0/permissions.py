from . import utils
import textwrap
import re

RE_ID = re.compile(r"^[0-9]+$")
RE_MODE = re.compile(r"^(0o)?([0-7]{3})$")


def check_path(path):
    out = f"""
    if not pathlib.Path("{path}").exists():
        raise Exception(f"Path [{path}] does not exist")
    """
    return textwrap.dedent(out)


def check_empty(path, force=False):
    out = f"""
    if any(pathlib.Path("{path}").iterdir()):
        if not {force}:
            raise Exception(
                f"Path [{path}] is not empty, skipping... Use [force=True] to override"
            )
    """
    return textwrap.dedent(out)


def chown(path, uid, gid, force=False):
    if not RE_ID.match(str(uid)):
        utils.throw_error(f"User ID must be a number, but got [{uid}]")
    if not RE_ID.match(str(gid)):
        utils.throw_error(f"Group ID must be a number, but got [{gid}]")

    out = f"""
    {check_path(path)}
    {check_empty(path, force)}
    os.chown("{path}", {int(uid)}, {int(gid)})
    """
    return textwrap.dedent(out)


def chmod(path, mode, force=False):
    if not RE_MODE.match(mode):
        utils.throw_error(
            f"Mode must be in octal format, but got [{mode}]. Example: 0o755 or 755"
        )

    out = f"""
    {check_path(path)}
    {check_empty(path, force)}
    os.chmod("{path}", {int(mode, 8)})
    """
    return textwrap.dedent(out)
