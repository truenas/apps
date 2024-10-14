from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from render import Render


try:
    from .error import RenderError
    from .volumes import Volume
    from .validations import valid_host_path_propagation, valid_octal_mode
except ImportError:
    from error import RenderError
    from volumes import Volume
    from validations import valid_host_path_propagation, valid_octal_mode


class BindMountType:
    def __init__(self, render_instance: "Render", vol: Volume):
        self._render_instance = render_instance
        self._vol: Volume = vol

        config = vol.config
        propagation = valid_host_path_propagation(config.get("propagation", "rprivate"))
        create_host_path = config.get("create_host_path", False)

        self._bind_mount_type_spec: dict = {
            "bind": {
                "create_host_path": create_host_path,
                "propagation": propagation,
            }
        }

    def render(self) -> dict:
        """Render the bind mount specification."""
        return self._bind_mount_type_spec


class VolumeMountType:
    def __init__(self, render_instance: "Render", vol: Volume):
        self._render_instance = render_instance
        self._vol: Volume = vol

        config = vol.config

        self._volume_mount_type_spec: dict = {"volume": {"nocopy": config.get("nocopy", False)}}

    def render(self) -> dict:
        """Render the volume mount specification."""
        return self._volume_mount_type_spec


# FIXME: remove
class TmpfsMountType:
    def __init__(self, render_instance: "Render", vol: Volume):
        self._render_instance = render_instance
        self._vol: Volume = vol

        config = vol.config
        size = config.get("size", None)
        mode = config.get("mode", None)

        spec = {"tmpfs": {}}

        if size is not None:
            if not isinstance(size, int):
                raise RenderError(f"Expected [size] to be an integer for [tmpfs] type, got [{size}]")
            if not size > 0:
                raise RenderError(f"Expected [size] to be greater than 0 for [tmpfs] type, got [{size}]")
            # Convert Mebibytes to Bytes
            spec["tmpfs"]["size"] = size * 1024 * 1024
        if mode is not None:
            mode = valid_octal_mode(mode)
            spec["tmpfs"]["mode"] = int(mode, 8)

        if not spec["tmpfs"]:
            spec.pop("tmpfs")

        self._tmpfs_mount_type_spec: dict = spec

    def render(self) -> dict:
        """Render the tmpfs mount specification."""
        return self._tmpfs_mount_type_spec


class TmpfsVolumeMount:
    def __init__(self, render_instance: "Render", config: dict):
        self._render_instance = render_instance
        self.spec = {"tmpfs": {}}
        size = config.get("size", None)
        mode = config.get("mode", None)

        if size is not None:
            if not isinstance(size, int):
                raise RenderError(f"Expected [size] to be an integer for [tmpfs] type, got [{size}]")
            if not size > 0:
                raise RenderError(f"Expected [size] to be greater than 0 for [tmpfs] type, got [{size}]")
            # Convert Mebibytes to Bytes
            self.spec["tmpfs"]["size"] = size * 1024 * 1024

        if mode is not None:
            # TODO: verify that the mode is valid
            mode = valid_octal_mode(mode)
            self.spec["tmpfs"]["mode"] = int(mode, 8)

        if not self.spec["tmpfs"]:
            self.spec.pop("tmpfs")

    def render(self) -> dict:
        """Render the tmpfs mount specification."""
        return self.spec


class BindVolumeMount:
    def __init__(self, render_instance: "Render", config: dict):
        self._render_instance = render_instance
        self.spec: dict = {}

        propagation = valid_host_path_propagation(config.get("propagation", "rprivate"))
        create_host_path = config.get("create_host_path", False)

        self.spec: dict = {
            "bind": {
                "create_host_path": create_host_path,
                "propagation": propagation,
            }
        }

    def render(self) -> dict:
        """Render the bind mount specification."""
        return self.spec
