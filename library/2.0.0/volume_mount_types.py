from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from render import Render
    from storage import IxStorageTmpfsConfig, IxStorageVolumeConfig, IxStorageBindLikeConfigs


try:
    from .error import RenderError
    from .validations import valid_host_path_propagation, valid_octal_mode_or_raise
except ImportError:
    from error import RenderError
    from validations import valid_host_path_propagation, valid_octal_mode_or_raise


class TmpfsMountType:
    def __init__(self, render_instance: "Render", config: "IxStorageTmpfsConfig"):
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
            mode = valid_octal_mode_or_raise(mode)
            self.spec["tmpfs"]["mode"] = int(mode, 8)

        if not self.spec["tmpfs"]:
            self.spec.pop("tmpfs")

    def render(self) -> dict:
        """Render the tmpfs mount specification."""
        return self.spec


class BindMountType:
    def __init__(self, render_instance: "Render", config: "IxStorageBindLikeConfigs"):
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


class VolumeMountType:
    def __init__(self, render_instance: "Render", config: "IxStorageVolumeConfig"):
        self._render_instance = render_instance
        self.spec: dict = {}

        self.spec: dict = {"volume": {"nocopy": config.get("nocopy", False)}}

    def render(self) -> dict:
        """Render the volume mount specification."""
        return self.spec
