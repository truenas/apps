from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from render import Render

try:
    from .dir.bind_mount import BindMount
    from .error import RenderError
    from .volumes import Volumes, Volume
    from .validations import valid_host_path_propagation, valid_fs_path_or_raise
except ImportError:
    from dir.bind_mount import BindMount
    from error import RenderError
    from volumes import Volumes, Volume
    from validations import valid_host_path_propagation, valid_fs_path_or_raise


class VolumeMounts:
    # We need the volumes here, so we can get the config and other info
    def __init__(self, render_instance: "Render", volumes: Volumes):
        self._render_instance = render_instance
        self._volumes = volumes
        self._volume_mounts: list[VolumeMount] = []
        self._mount_targets: set[str] = set()

    def add_volume_mount(self, vol_identifier: str, mount_path: str):
        mount_path = valid_fs_path_or_raise(mount_path.rstrip("/"))
        if vol_identifier not in self._volumes.volume_identifiers():
            raise RenderError(
                f"Volume [{vol_identifier}] not found in defined volumes. "
                f"Available volumes: [{', '.join(self._volumes.volume_identifiers())}]"
            )

        if mount_path in self._mount_targets:
            raise RenderError(f"Container path [{mount_path}] already added")

        volume = self._volumes.get_volume(vol_identifier)
        volume_mount = VolumeMount(self._render_instance, mount_path, volume)
        self._volume_mounts.append(volume_mount)
        self._mount_targets.add(mount_path)

    def has_mounts(self) -> bool:
        """Check if there are any volume mounts defined."""
        return bool(self._volume_mounts)

    def render(self) -> list[dict]:
        """Render all volume mounts into a list of dictionaries."""
        return [v.render() for v in sorted(self._volume_mounts, key=lambda v: v.source)]


class VolumeMount:
    _mount_spec_classes = {
        "bind": BindMount,
    }

    def __init__(self, render_instance: "Render", mount_path: str, vol: Volume):
        self._render_instance = render_instance
        self._source = vol.source
        self._type = vol.mount_type
        self._read_only = vol.read_only
        self._spec: dict = {}
        self._common_spec = {
            "type": self._type,
            "source": self._source,
            "target": mount_path,
            "read_only": self.read_only,
        }

        mount_spec_class = self._mount_spec_classes.get(self._type)
        if not mount_spec_class:
            valid_types = ", ".join(self._mount_spec_classes.keys())
            raise RenderError(f"Volume type [{self._type}] is not valid. Valid options are: [{valid_types}]")

        mount_spec = mount_spec_class(self._render_instance, vol).render()
        self._spec = merge_dicts_no_overwrite(self._common_spec, mount_spec)

    @property
    def read_only(self) -> bool:
        return self._read_only

    @property
    def source(self) -> str:
        """Return the source path or volume name."""
        return self._source

    def render(self) -> dict:
        """Render the volume mount specification."""
        return self._spec


def merge_dicts_no_overwrite(dict1, dict2):
    overlapping_keys = dict1.keys() & dict2.keys()
    if overlapping_keys:
        raise ValueError(f"Merging of dicts failed. Overlapping keys: {overlapping_keys}")
    return {**dict1, **dict2}
