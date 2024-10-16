from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from render import Render

try:
    from .error import RenderError
    from .formatter import merge_dicts_no_overwrite
    from .volume_mount_types import BindMountType, VolumeMountType, TmpfsMountType
    from .validations import valid_fs_path_or_raise, valid_octal_mode_or_raise
    from .volume_sources import HostPathSource, IxVolumeSource, CifsSource, NfsSource, VolumeSource
except ImportError:
    from error import RenderError
    from formatter import merge_dicts_no_overwrite
    from volume_mount_types import BindMountType, VolumeMountType, TmpfsMountType
    from validations import valid_fs_path_or_raise, valid_octal_mode_or_raise
    from volume_sources import HostPathSource, IxVolumeSource, CifsSource, NfsSource, VolumeSource


class VolumeMounts:
    def __init__(self, render_instance: "Render"):
        self._render_instance = render_instance
        self._volume_mounts: set[VolumeMount] = set()

    def add(self, mount_path: str, config: dict, permission_config: dict | None = None):
        mount_path = valid_fs_path_or_raise(mount_path)
        if mount_path in [m.mount_path for m in self._volume_mounts]:
            raise RenderError(f"Mount path [{mount_path}] already used for another volume mount")

        volume_mount = VolumeMount(self._render_instance, mount_path, config)
        self._volume_mounts.add(volume_mount)

        source = volume_mount.volume_mount_spec.get("source", "")
        if not source:
            return

        action = self.parse_permissions_config(source, config, permission_config)
        if not action:
            return

        # Add the action to the permissions container
        self._render_instance._permissions_container.add_action(source=source, action=action)

    def parse_permissions_config(self, source: str, config: dict, permission_config: dict | None):
        if not permission_config:
            return

        # Volumes without source is not able to be shared across containers
        if not source:
            return

        # If the volume is an ix_volume, we need to set auto_permissions
        if config.get("ix_volume_config", {}):
            config["auto_permissions"] = True

        # Nothing to do if auto_permissions is disabled
        if not config.get("auto_permissions", False):
            return

        # ACL are always preferred and we should ignore auto_permissions
        if config.get("ix_volume_config", {}).get("acl_enable", False):
            return
        if config.get("host_path_config", {}).get("acl_enable", False):
            return

        is_temporary = permission_config.get("is_temporary", False)
        uid = permission_config.get("uid", None)
        gid = permission_config.get("gid", None)
        chmod = permission_config.get("chmod", None)
        mode = permission_config.get("mode", None)

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
            "config": config,
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


class VolumeMount:
    def __init__(self, render_instance: "Render", mount_path: str, config: dict):
        self._render_instance = render_instance
        self.mount_path: str = mount_path

        storage_type: str = config.get("type", "")
        if not storage_type:
            raise RenderError("Expected [type] to be set for volume mounts.")

        match storage_type:
            case "host_path":
                spec_type = "bind"
                mount_config = config.get("host_path_config", {}) or {}
                mount_type_specific_definition = BindMountType(self._render_instance, mount_config).render()
                source = HostPathSource(self._render_instance, mount_config).get()
            case "ix_volume":
                spec_type = "bind"
                mount_config = config.get("ix_volume_config", {}) or {}
                mount_type_specific_definition = BindMountType(self._render_instance, mount_config).render()
                source = IxVolumeSource(self._render_instance, mount_config).get()
            case "tmpfs":
                spec_type = "tmpfs"
                mount_config = config.get("tmpfs_config", {}) or {}
                mount_type_specific_definition = TmpfsMountType(self._render_instance, mount_config).render()
                source = None
            case "nfs":
                spec_type = "volume"
                mount_config = config.get("nfs_config", {}) or {}
                mount_type_specific_definition = VolumeMountType(self._render_instance, mount_config).render()
                source = NfsSource(self._render_instance, mount_config).get()
            case "cifs":
                spec_type = "volume"
                mount_config = config.get("cifs_config", {}) or {}
                mount_type_specific_definition = VolumeMountType(self._render_instance, mount_config).render()
                source = CifsSource(self._render_instance, mount_config).get()
            case "volume":
                spec_type = "volume"
                mount_config = config.get("volume_config", {}) or {}
                mount_type_specific_definition = VolumeMountType(self._render_instance, mount_config).render()
                source = VolumeSource(self._render_instance, mount_config).get()
            case "temporary" | "anonymous":
                spec_type = "volume"
                mount_config = config.get("volume_config", {}) or {}
                mount_type_specific_definition = VolumeMountType(self._render_instance, mount_config).render()
                source = None
            case _:
                raise RenderError(f"Storage type [{storage_type}] is not supported for volume mounts.")

        common_spec = {"type": spec_type, "target": self.mount_path, "read_only": config.get("read_only", False)}
        if source is not None:
            common_spec["source"] = source
            self._render_instance.volumes.add_volume(source, storage_type, mount_config)

        self.volume_mount_spec = merge_dicts_no_overwrite(common_spec, mount_type_specific_definition)

    def render(self) -> dict:
        return self.volume_mount_spec
