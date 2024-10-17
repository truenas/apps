import copy
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from render import Render

try:
    from .error import RenderError
    from .validations import valid_fs_path_or_raise, valid_octal_mode_or_raise
    from .volume_mount import VolumeMount
except ImportError:
    from error import RenderError
    from validations import valid_fs_path_or_raise, valid_octal_mode_or_raise
    from volume_mount import VolumeMount


class Storage:
    def __init__(self, render_instance: "Render"):
        self._render_instance = render_instance
        self._volume_mounts: set[VolumeMount] = set()

    def add(self, mount_path: str, config: dict, permission_config: dict | None = None):
        mount_path = valid_fs_path_or_raise(mount_path)
        if mount_path in [m.mount_path for m in self._volume_mounts]:
            raise RenderError(f"Mount path [{mount_path}] already used for another volume mount")

        volume_mount = VolumeMount(self._render_instance, mount_path, config)
        self._volume_mounts.add(volume_mount)

        # Volumes without source is not able to be shared across containers
        source = volume_mount.volume_mount_spec.get("source", "")
        if not source:
            return

        action = self.parse_permissions_config(source, config, permission_config)
        if not action:
            return
        # Add the action to the permissions container
        self._render_instance._permissions_container.add_action(source=source, action=action)

    def parse_permissions_config(self, source: str, config: dict, permission_config: dict | None):
        perm_config = copy.deepcopy(permission_config) or {}
        vol_config = copy.deepcopy(config) or {}

        if not perm_config:
            return

        # Volumes without source is not able to be shared across containers
        if not source:
            return

        if vol_config.get("type", "") == "temporary":
            perm_config["is_temporary"] = True

        # If the volume is an ix_volume, we need to set auto_permissions
        if vol_config.get("ix_volume_config", {}):
            vol_config["auto_permissions"] = True

        # Nothing to do if auto_permissions is disabled
        if not vol_config.get("auto_permissions", False):
            return

        # ACL are always preferred and we should ignore auto_permissions
        if vol_config.get("ix_volume_config", {}).get("acl_enable", False):
            return
        if vol_config.get("host_path_config", {}).get("acl_enable", False):
            return

        is_temporary = perm_config.get("is_temporary", False)
        uid = perm_config.get("uid", None)
        gid = perm_config.get("gid", None)
        chmod = perm_config.get("chmod", None)
        mode = perm_config.get("mode", None)

        if not isinstance(is_temporary, bool):
            raise RenderError("Expected [is_temporary] to be a boolean")

        if not isinstance(uid, int) or not isinstance(gid, int):
            raise RenderError("Expected [uid] and [gid] to be set when [auto_permissions] is enabled")

        if chmod is not None:
            chmod = valid_octal_mode_or_raise(chmod)

        valid_modes = ["always", "check"]
        if mode not in valid_modes:
            raise RenderError(f"Expected [mode] to be one of [{', '.join(valid_modes)}], got [{mode}]")

        return {
            "config": vol_config,
            "source": source,
            "uid": uid,
            "gid": gid,
            "chmod": chmod,
            "mode": mode,
            "is_temporary": is_temporary,
        }

    def has_mounts(self) -> bool:
        return bool(self._volume_mounts)

    def render(self):
        return [vm.render() for vm in sorted(self._volume_mounts, key=lambda vm: vm.mount_path)]
