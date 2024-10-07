try:
    from .error import RenderError
    from .validations import must_be_valid_path, must_not_be_disallowed_device
except ImportError:
    from error import RenderError
    from validations import must_be_valid_path, must_not_be_disallowed_device


class Device:
    def __init__(self, host_device: str, container_device: str, allow_disallowed=False):
        hd = host_device.rstrip("/")
        cd = container_device.rstrip("/")
        if not hd or not cd:
            raise RenderError(
                "Expected [host_device] and [container_device] to be set. "
                f"Got host_device [{host_device}] and container_device [{container_device}]"
            )

        must_be_valid_path(host_device)
        must_be_valid_path(container_device)
        if not allow_disallowed:
            must_not_be_disallowed_device(hd)

        self.host_device: str = hd
        self.container_device: str = cd

    def render(self):
        return f"{self.host_device}:{self.container_device}"


class Devices:
    def __init__(self, render_instance):
        self.render_instance = render_instance
        self.devices: set[Device] = set()

        self._container_devices: set[str] = set()
        # Scan values for devices we should automatically add
        # for example /dev/dri for gpus
        self.add_devices_from_values()

    def add_devices_from_values(self):
        resources = self.render_instance.values.get("resources", {})

        if resources.get("gpus", {}).get("use_all_gpus", False):
            self.add_device("/dev/dri", "/dev/dri", allow_disallowed=True)
            self._container_devices.add("/dev/dri")

    def add_device(self, host_device: str, container_device: str, allow_disallowed=False):
        device = Device(host_device, container_device, allow_disallowed)
        # Host device can be mapped to multiple container devices,
        # so we only make sure container devices are not duplicated
        if device.container_device in self._container_devices:
            raise RenderError(
                f"Device with container path [{device.container_device}] already added"
            )

        self.devices.add(device)
        self._container_devices.add(device.container_device)

    def has_devices(self):
        return len(self.devices) > 0

    def render(self) -> list[str]:
        return [d.render() for d in self.devices]
