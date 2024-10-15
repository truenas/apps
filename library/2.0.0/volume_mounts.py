from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from render import Render

try:
    from .error import RenderError
    from .formatter import merge_dicts_no_overwrite
    from .validations import valid_fs_path_or_raise
    from .storage_types import (
        AnonymousVolumeStorage,
        CifsStorage,
        DockerVolumeStorage,
        HostPathStorage,
        IxVolumeStorage,
        NfsStorage,
        StorageItemResult,
        TmpfsStorage,
    )
except ImportError:
    from error import RenderError
    from formatter import merge_dicts_no_overwrite
    from validations import valid_fs_path_or_raise
    from storage_types import (
        AnonymousVolumeStorage,
        CifsStorage,
        DockerVolumeStorage,
        HostPathStorage,
        IxVolumeStorage,
        NfsStorage,
        StorageItemResult,
        TmpfsStorage,
    )


class VolumeMounts:
    def __init__(self, render_instance: "Render"):
        self._render_instance = render_instance
        self._volume_mounts: set[VolumeMount] = set()

    def add_volume_mount(self, mount_path: str, config: dict):
        mount_path = valid_fs_path_or_raise(mount_path)
        if mount_path in [m.mount_path for m in self._volume_mounts]:
            raise RenderError(f"Mount path [{mount_path}] already used for another volume mount")

        volume_mount = VolumeMount(self._render_instance, mount_path, config)
        self._volume_mounts.add(volume_mount)

    def has_mounts(self) -> bool:
        return bool(self._volume_mounts)

    def render(self):
        return [vm.render() for vm in sorted(self._volume_mounts, key=lambda vm: vm.mount_path)]


class VolumeMount:
    # TODO: create a type for config
    def __init__(self, render_instance: "Render", mount_path: str, config: dict):
        self._render_instance = render_instance
        self.mount_path: str = mount_path
        self.read_only: bool = config.get("read_only", False)

        self.source: str | None = None  # tmpfs does not have a source
        self.spec_type: str = ""

        self.spec_config_for_type: dict = {}

        self.volume_mount_spec: dict = {}

        _type_spec_mapping = {
            "anonymous": {"class": AnonymousVolumeStorage, "spec_type": "volume"},
            "cifs": {"class": CifsStorage, "spec_type": "volume"},
            "host_path": {"class": HostPathStorage, "spec_type": "bind"},
            "ix_volume": {"class": IxVolumeStorage, "spec_type": "bind"},
            "nfs": {"class": NfsStorage, "spec_type": "volume"},
            "tmpfs": {"class": TmpfsStorage, "spec_type": "tmpfs"},
            "volume": {"class": DockerVolumeStorage, "spec_type": "volume"},
            # TODO: temporary volumes
        }

        vol_type = config.get("type", None)
        if vol_type not in _type_spec_mapping:
            valid_types = ", ".join(_type_spec_mapping.keys())
            raise RenderError(f"Volume type [{vol_type}] is not valid. Valid options are: [{valid_types}]")

        # Parse the config for the type
        storage_item: StorageItemResult = _type_spec_mapping[vol_type]["class"](self._render_instance, config).render()

        # Set the type in the mount type for the spec
        self.spec_type = _type_spec_mapping[vol_type]["spec_type"]

        # Make sure source is not empty for all but tmpfs and anonymous
        if self.spec_type != "tmpfs" and vol_type != "anonymous":
            if not storage_item.source:
                raise RenderError(f"Missing source for volume type [{vol_type}]")

        # Fetch the source (path for bind, volume name for volume)
        self.source = storage_item.source
        if vol_type == "anonymous":
            # anonymous have no source.
            self.source = None

        # Fetch the type specific config for the mount spec
        self.spec_config_for_type = storage_item.mount_spec

        # No source or volume spec for anonymous
        if self.spec_type == "volume" and vol_type != "anonymous":
            assert self.source is not None
            assert storage_item.volume_spec is not None
            self._render_instance.volumes.add_volume(self.source, storage_item.volume_spec)

    def render(self) -> dict:
        result = {
            "target": self.mount_path,
            "read_only": self.read_only,
        }

        if self.spec_type is not None:
            result["type"] = self.spec_type

        if self.source is not None:
            result["source"] = self.source

        if self.spec_config_for_type:
            result = merge_dicts_no_overwrite(result, self.spec_config_for_type)

        return result
