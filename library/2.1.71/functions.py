import re
import copy
import yaml
import bcrypt
import secrets
import urllib.parse
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

    def _to_yaml(self, data):
        return yaml.dump(data)

    def _bcrypt_hash(self, password):
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        return hashed

    def _htpasswd(self, username, password):
        hashed = self._bcrypt_hash(password)
        return username + ":" + hashed

    def _secure_string(self, length):
        return secrets.token_urlsafe(length)[:length]

    def _basic_auth(self, username, password):
        return b64encode(f"{username}:{password}".encode("utf-8")).decode("utf-8")

    def _basic_auth_header(self, username, password):
        return f"Basic {self._basic_auth(username, password)}"

    def _fail(self, message):
        raise RenderError(message)

    def _camel_case(self, string):
        return string.title()

    def _auto_cast(self, value):
        lower_str_value = str(value).lower()
        if lower_str_value in ["true", "false"]:
            return lower_str_value == "true"

        try:
            float_value = float(value)
            if float_value.is_integer():
                return int(float_value)
            else:
                return float(value)
        except ValueError:
            pass

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
        return copy.deepcopy(dict)

    def _deep_merge(self, dict1: dict, dict2: dict):
        """
        Deep merge: recursively merges nested dictionaries.
        Values from dict2 override values from dict1.
        Nested dicts are merged recursively rather than replaced.
        """
        result = dict1.copy()

        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Both values are dicts - merge them recursively
                result[key] = self._deep_merge(result[key], value)
            else:
                # Either not both dicts, or key doesn't exist - use dict2's value
                result[key] = value

        return result

    def _disallow_chars(self, string: str, chars: list[str], key: str):
        for char in chars:
            if char in string:
                raise RenderError(f"Disallowed character [{char}] in [{key}]")
        return string

    def _or_default(self, value, default):
        if not value:
            return default
        return value

    def _url_to_dict(self, url: str, v6_brackets: bool = False):
        try:
            # Try parsing as-is first
            parsed = urllib.parse.urlparse(url)

            # If we didn't get a hostname, try with http:// prefix
            if not parsed.hostname:
                parsed = urllib.parse.urlparse(f"http://{url}")

            # Final check that we have a valid result
            if not parsed.hostname:
                raise RenderError(
                    f"Failed to parse URL [{url}]. Ensure it is a valid URL with a hostname and optional port."
                )

            result = {
                "netloc": parsed.netloc,
                "scheme": parsed.scheme,
                "host": parsed.hostname,
                "port": parsed.port,
                "path": parsed.path,
            }
            if v6_brackets and parsed.hostname and ":" in parsed.hostname:
                result["host"] = f"[{parsed.hostname}]"
                result["host_no_brackets"] = parsed.hostname

            return result

        except Exception:
            raise RenderError(
                f"Failed to parse URL [{url}]. Ensure it is a valid URL with a hostname and optional port."
            )

    def _require_unique(self, values, key, split_char=""):
        new_values = []
        for value in values:
            new_values.append(value.split(split_char)[0] if split_char else value)

        if len(new_values) != len(set(new_values)):
            raise RenderError(f"Expected values in [{key}] to be unique, but got [{', '.join(values)}]")

    def _require_no_reserved(self, values, key, reserved, split_char="", starts_with=False):
        new_values = []
        for value in values:
            new_values.append(value.split(split_char)[0] if split_char else value)

        if starts_with:
            for arg in new_values:
                for reserved_value in reserved:
                    if arg.startswith(reserved_value):
                        raise RenderError(f"Value [{reserved_value}] is reserved and cannot be set in [{key}]")
            return

        for reserved_value in reserved:
            if reserved_value in new_values:
                raise RenderError(f"Value [{reserved_value}] is reserved and cannot be set in [{key}]")

    def _url_encode(self, string):
        return urllib.parse.quote_plus(string)

    def _temp_config(self, name):
        if not name:
            raise RenderError("Expected [name] to be set when calling [temp_config].")
        return {"type": "temporary", "volume_config": {"volume_name": name}}

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
            "deep_merge": self._deep_merge,
            "must_match_regex": self._must_match_regex,
            "secure_string": self._secure_string,
            "disallow_chars": self._disallow_chars,
            "get_host_path": self._get_host_path,
            "or_default": self._or_default,
            "temp_config": self._temp_config,
            "require_unique": self._require_unique,
            "require_no_reserved": self._require_no_reserved,
            "url_encode": self._url_encode,
            "url_to_dict": self._url_to_dict,
            "to_yaml": self._to_yaml,
        }
