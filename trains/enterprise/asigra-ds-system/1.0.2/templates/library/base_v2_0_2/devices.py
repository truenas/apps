from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from render import Render

try:
    from .error import RenderError
    from .device import Device
except ImportError:
    from error import RenderError
    from device import Device


class Devices:
    def __init__(self, render_instance: "Render"):
        self._render_instance = render_instance
        self._devices: set[Device] = set()

        # Tracks all container device paths to make sure they are not duplicated
        self._container_device_paths: set[str] = set()
        # Scan values for devices we should automatically add
        # for example /dev/dri for gpus
        self._auto_add_devices_from_values()

    def _auto_add_devices_from_values(self):
        resources = self._render_instance.values.get("resources", {})

        if resources.get("gpus", {}).get("use_all_gpus", False):
            self.add_device("/dev/dri", "/dev/dri", allow_disallowed=True)
            self._container_device_paths.add("/dev/dri")

    def add_device(self, host_device: str, container_device: str, cgroup_perm: str = "", allow_disallowed=False):
        # Host device can be mapped to multiple container devices,
        # so we only make sure container devices are not duplicated
        if container_device in self._container_device_paths:
            raise RenderError(f"Device with container path [{container_device}] already added")

        self._devices.add(Device(host_device, container_device, cgroup_perm, allow_disallowed))
        self._container_device_paths.add(container_device)

    def has_devices(self):
        return len(self._devices) > 0

    def render(self) -> list[str]:
        return sorted([d.render() for d in self._devices])
