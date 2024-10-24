from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from render import Render
    from storage import IxStorage

try:
    from .error import RenderError
    from .formatter import merge_dicts_no_overwrite
    from .volume_mount_types import BindMountType, VolumeMountType, TmpfsMountType
    from .volume_sources import HostPathSource, IxVolumeSource, CifsSource, NfsSource, VolumeSource
except ImportError:
    from error import RenderError
    from formatter import merge_dicts_no_overwrite
    from volume_mount_types import BindMountType, VolumeMountType, TmpfsMountType
    from volume_sources import HostPathSource, IxVolumeSource, CifsSource, NfsSource, VolumeSource


class VolumeMount:
    def __init__(self, render_instance: "Render", mount_path: str, config: "IxStorage"):
        self._render_instance = render_instance
        self.mount_path: str = mount_path

        storage_type: str = config.get("type", "")
        if not storage_type:
            raise RenderError("Expected [type] to be set for volume mounts.")

        match storage_type:
            case "host_path":
                spec_type = "bind"
                mount_config = config.get("host_path_config")
                assert mount_config is not None
                mount_type_specific_definition = BindMountType(self._render_instance, mount_config).render()
                source = HostPathSource(self._render_instance, mount_config).get()
            case "ix_volume":
                spec_type = "bind"
                mount_config = config.get("ix_volume_config")
                assert mount_config is not None
                mount_type_specific_definition = BindMountType(self._render_instance, mount_config).render()
                source = IxVolumeSource(self._render_instance, mount_config).get()
            case "tmpfs":
                spec_type = "tmpfs"
                mount_config = config.get("tmpfs_config", {})
                mount_type_specific_definition = TmpfsMountType(self._render_instance, mount_config).render()
                source = None
            case "nfs":
                spec_type = "volume"
                mount_config = config.get("nfs_config")
                assert mount_config is not None
                mount_type_specific_definition = VolumeMountType(self._render_instance, mount_config).render()
                source = NfsSource(self._render_instance, mount_config).get()
            case "cifs":
                spec_type = "volume"
                mount_config = config.get("cifs_config")
                assert mount_config is not None
                mount_type_specific_definition = VolumeMountType(self._render_instance, mount_config).render()
                source = CifsSource(self._render_instance, mount_config).get()
            case "volume":
                spec_type = "volume"
                mount_config = config.get("volume_config")
                assert mount_config is not None
                mount_type_specific_definition = VolumeMountType(self._render_instance, mount_config).render()
                source = VolumeSource(self._render_instance, mount_config).get()
            case "temporary" | "anonymous":
                spec_type = "volume"
                mount_config = config.get("volume_config")
                assert mount_config is not None
                mount_type_specific_definition = VolumeMountType(self._render_instance, mount_config).render()
                source = None
            case _:
                raise RenderError(f"Storage type [{storage_type}] is not supported for volume mounts.")

        common_spec = {"type": spec_type, "target": self.mount_path, "read_only": config.get("read_only", False)}
        if source is not None:
            common_spec["source"] = source
            self._render_instance.volumes.add_volume(source, storage_type, mount_config)  # type: ignore

        self.volume_mount_spec = merge_dicts_no_overwrite(common_spec, mount_type_specific_definition)

    def render(self) -> dict:
        return self.volume_mount_spec
