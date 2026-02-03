import json
import pathlib
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from render import Render
    from storage import IxStorage

try:
    from .error import RenderError
    from .validations import valid_octal_mode_or_raise, valid_fs_path_or_raise
except ImportError:
    from error import RenderError
    from validations import valid_octal_mode_or_raise, valid_fs_path_or_raise


class PermsContainer:
    def __init__(self, render_instance: "Render", name: str):
        self._render_instance = render_instance
        self._name = name
        self.actions: set[str] = set()
        self.parsed_configs: list[dict] = []

    def add_or_skip_action(self, identifier: str, volume_config: "IxStorage", action_config: dict):
        identifier = self.normalize_identifier_for_path(identifier)
        if identifier in self.actions:
            raise RenderError(f"Action with id [{identifier}] already used for another permission action")

        parsed_action = self.parse_action(identifier, volume_config, action_config)
        if parsed_action:
            self.parsed_configs.append(parsed_action)
            self.actions.add(identifier)

    def parse_action(self, identifier: str, volume_config: "IxStorage", action_config: dict):
        valid_modes = [
            "always",  # Always set permissions, without checking.
            "check",  # Checks if permissions are correct, and set them if not.
        ]
        mode = action_config.get("mode", "check")
        uid = action_config.get("uid", None)
        gid = action_config.get("gid", None)
        chmod = action_config.get("chmod", None)
        recursive = action_config.get("recursive", False)
        mount_path = pathlib.Path("/mnt/permission", identifier).as_posix()
        read_only = volume_config.get("read_only", False)
        is_temporary = False

        vol_type = volume_config.get("type", "")
        match vol_type:
            case "temporary":
                # If it is a temporary volume, we force auto permissions
                # and set is_temporary to True, so it will be cleaned up
                is_temporary = True
                recursive = True
            case "volume":
                if not volume_config.get("volume_config", {}).get("auto_permissions", False):
                    return None
            case "host_path":
                host_path_config = volume_config.get("host_path_config", {})
                # Skip when ACL enabled
                if host_path_config.get("acl_enable", False):
                    return None
                if not host_path_config.get("auto_permissions", False):
                    return None
            case "ix_volume":
                ix_vol_config = volume_config.get("ix_volume_config", {})
                # Skip when ACL enabled
                if ix_vol_config.get("acl_enable", False):
                    return None
                # For ix_volumes, we default to auto_permissions = True
                if not ix_vol_config.get("auto_permissions", True):
                    return None
            case _:
                # Skip for other types
                return None

        if mode not in valid_modes:
            raise RenderError(f"Expected [mode] to be one of [{', '.join(valid_modes)}], got [{mode}]")
        if not isinstance(uid, int) or not isinstance(gid, int):
            raise RenderError("Expected [uid] and [gid] to be set when [auto_permissions] is enabled")
        if chmod is not None:
            chmod = valid_octal_mode_or_raise(chmod)

        mount_path = valid_fs_path_or_raise(mount_path)
        return {
            "mount_path": mount_path,
            "volume_config": volume_config,
            "action_data": {
                "read_only": read_only,
                "mount_path": mount_path,
                "is_temporary": is_temporary,
                "identifier": identifier,
                "recursive": recursive,
                "mode": mode,
                "uid": uid,
                "gid": gid,
                "chmod": chmod,
            },
        }

    def normalize_identifier_for_path(self, identifier: str):
        return identifier.rstrip("/").lstrip("/").lower().replace("/", "_").replace(".", "-").replace(" ", "-")

    def has_actions(self):
        return bool(self.actions)

    def activate(self):
        if len(self.parsed_configs) != len(self.actions):
            raise RenderError("Number of actions and parsed configs does not match")

        if not self.has_actions():
            raise RenderError("No actions added. Check if there are actions before activating")

        # Add the container and set it up
        c = self._render_instance.add_container(self._name, "container_utils_image")
        c.set_user(0, 0)
        c.add_caps(["CHOWN", "FOWNER", "DAC_OVERRIDE"])
        c.set_network_mode("none")

        # Don't attach any devices
        c.remove_devices()

        c.deploy.resources.set_profile("medium")
        c.restart.set_policy("on-failure", maximum_retry_count=1)
        c.healthcheck.disable()

        c.set_entrypoint(["python3", "/script/permissions.py"])

        actions_data: list[dict] = []
        for parsed in self.parsed_configs:
            if not parsed["action_data"]["read_only"]:
                c.add_storage(parsed["mount_path"], parsed["volume_config"])
            actions_data.append(parsed["action_data"])

        actions_data_json = json.dumps(actions_data)
        c.configs.add("permissions_actions_data", actions_data_json, "/script/actions.json", "0500")
