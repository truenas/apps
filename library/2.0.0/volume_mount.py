from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from render import Render

try:
    from .bind_mount import BindMount
    from .error import RenderError
    from .volumes import Volume
except ImportError:
    from bind_mount import BindMount
    from error import RenderError
    from volumes import Volume


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
