from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from render import Render

try:
    from .error import RenderError
    from .volumes import Volumes
    from .volume_mount import VolumeMount
    from .validations import valid_fs_path_or_raise
except ImportError:
    from error import RenderError
    from volumes import Volumes
    from volume_mount import VolumeMount
    from validations import valid_fs_path_or_raise


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
