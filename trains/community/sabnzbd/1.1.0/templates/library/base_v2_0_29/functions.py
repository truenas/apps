import re
import bcrypt
import secrets
from base64 import b64encode
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from render import Render

try:
    from .error import RenderError
    from .volume_sources import HostPathSource, IxVolumeSource
except ImportError:
    from error import RenderError
    from volume_sources import HostPathSource, IxVolumeSource


class Functions:
    def __init__(self, render_instance: "Render"):
        self._render_instance = render_instance

    def _bcrypt_hash(self, password):
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        return hashed

    def _htpasswd(self, username, password):
        hashed = self._bcrypt_hash(password)
        return username + ":" + hashed

    def _secure_string(self, length):
        return secrets.token_urlsafe(length)

    def _basic_auth(self, username, password):
        return b64encode(f"{username}:{password}".encode("utf-8")).decode("utf-8")

    def _basic_auth_header(self, username, password):
        return f"Basic {self._basic_auth(username, password)}"

    def _fail(self, message):
        raise RenderError(message)

    def _camel_case(self, string):
        return string.title()

    def _auto_cast(self, value):
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

    def _match_regex(self, value, regex):
        if not re.match(regex, value):
            return False
        return True

    def _must_match_regex(self, value, regex):
        if not self._match_regex(value, regex):
            raise RenderError(f"Expected [{value}] to match [{regex}]")
        return value

    def _is_boolean(self, string):
        return string.lower() in ["true", "false"]

    def _is_number(self, string):
        try:
            float(string)
            return True
        except ValueError:
            return False

    def _copy_dict(self, dict):
        return dict.copy()

    def _merge_dicts(self, *dicts):
        merged_dict = {}
        for dictionary in dicts:
            merged_dict.update(dictionary)
        return merged_dict

    def _disallow_chars(self, string: str, chars: list[str], key: str):
        for char in chars:
            if char in string:
                raise RenderError(f"Disallowed character [{char}] in [{key}]")
        return string

    def _get_host_path(self, storage):
        source_type = storage.get("type", "")
        if not source_type:
            raise RenderError("Expected [type] to be set for volume mounts.")

        match source_type:
            case "host_path":
                mount_config = storage.get("host_path_config")
                if mount_config is None:
                    raise RenderError("Expected [host_path_config] to be set for [host_path] type.")
                host_source = HostPathSource(self._render_instance, mount_config).get()
                return host_source
            case "ix_volume":
                mount_config = storage.get("ix_volume_config")
                if mount_config is None:
                    raise RenderError("Expected [ix_volume_config] to be set for [ix_volume] type.")
                ix_source = IxVolumeSource(self._render_instance, mount_config).get()
                return ix_source
            case _:
                raise RenderError(f"Storage type [{source_type}] does not support host path.")

    def func_map(self):
        # TODO: Check what is no longer used and remove
        return {
            "auto_cast": self._auto_cast,
            "basic_auth_header": self._basic_auth_header,
            "basic_auth": self._basic_auth,
            "bcrypt_hash": self._bcrypt_hash,
            "camel_case": self._camel_case,
            "copy_dict": self._copy_dict,
            "fail": self._fail,
            "htpasswd": self._htpasswd,
            "is_boolean": self._is_boolean,
            "is_number": self._is_number,
            "match_regex": self._match_regex,
            "merge_dicts": self._merge_dicts,
            "must_match_regex": self._must_match_regex,
            "secure_string": self._secure_string,
            "disallow_chars": self._disallow_chars,
            "get_host_path": self._get_host_path,
        }
