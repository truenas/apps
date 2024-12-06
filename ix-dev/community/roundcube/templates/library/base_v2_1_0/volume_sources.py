from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from render import Render
    from storage import IxStorageHostPathConfig, IxStorageIxVolumeConfig, IxStorageVolumeConfig

try:
    from .error import RenderError
    from .formatter import get_hashed_name_for_volume
    from .validations import valid_fs_path_or_raise
except ImportError:
    from error import RenderError
    from formatter import get_hashed_name_for_volume
    from validations import valid_fs_path_or_raise


class HostPathSource:
    def __init__(self, render_instance: "Render", config: "IxStorageHostPathConfig"):
        self._render_instance = render_instance
        self.source: str = ""

        if not config:
            raise RenderError("Expected [host_path_config] to be set for [host_path] type.")

        path = ""
        if config.get("acl_enable", False):
            acl_path = config.get("acl", {}).get("path")
            if not acl_path:
                raise RenderError("Expected [host_path_config.acl.path] to be set for [host_path] type.")
            path = valid_fs_path_or_raise(acl_path)
        else:
            path = valid_fs_path_or_raise(config.get("path", ""))

        self.source = path.rstrip("/")

    def get(self):
        return self.source


class IxVolumeSource:
    def __init__(self, render_instance: "Render", config: "IxStorageIxVolumeConfig"):
        self._render_instance = render_instance
        self.source: str = ""

        if not config:
            raise RenderError("Expected [ix_volume_config] to be set for [ix_volume] type.")
        dataset_name = config.get("dataset_name")
        if not dataset_name:
            raise RenderError("Expected [ix_volume_config.dataset_name] to be set for [ix_volume] type.")

        ix_volumes = self._render_instance.values.get("ix_volumes", {})
        if dataset_name not in ix_volumes:
            available = ", ".join(ix_volumes.keys())
            raise RenderError(
                f"Expected the key [{dataset_name}] to be set in [ix_volumes] for [ix_volume] type. "
                f"Available keys: [{available}]."
            )

        self.source = valid_fs_path_or_raise(ix_volumes[dataset_name].rstrip("/"))

    def get(self):
        return self.source


class CifsSource:
    def __init__(self, render_instance: "Render", config: dict):
        self._render_instance = render_instance
        self.source: str = ""

        if not config:
            raise RenderError("Expected [cifs_config] to be set for [cifs] type.")
        self.source = get_hashed_name_for_volume("cifs", config)

    def get(self):
        return self.source


class NfsSource:
    def __init__(self, render_instance: "Render", config: dict):
        self._render_instance = render_instance
        self.source: str = ""

        if not config:
            raise RenderError("Expected [nfs_config] to be set for [nfs] type.")
        self.source = get_hashed_name_for_volume("nfs", config)

    def get(self):
        return self.source


class VolumeSource:
    def __init__(self, render_instance: "Render", config: "IxStorageVolumeConfig"):
        self._render_instance = render_instance
        self.source: str = ""

        if not config:
            raise RenderError("Expected [volume_config] to be set for [volume] type.")

        volume_name: str = config.get("volume_name", "")
        if not volume_name:
            raise RenderError("Expected [volume_config.volume_name] to be set for [volume] type.")

        self.source = volume_name

    def get(self):
        return self.source
