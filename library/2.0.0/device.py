try:
    from .error import RenderError
    from .validations import must_be_valid_path, must_not_be_disallowed_device, must_be_valid_cgroup_perm
except ImportError:
    from error import RenderError
    from validations import must_be_valid_path, must_not_be_disallowed_device, must_be_valid_cgroup_perm


class Device:
    def __init__(self, host_device: str, container_device: str, cgroup_perm: str = "", allow_disallowed=False):
        hd = host_device.rstrip("/")
        cd = container_device.rstrip("/")
        if not hd or not cd:
            raise RenderError(
                "Expected [host_device] and [container_device] to be set. "
                f"Got host_device [{host_device}] and container_device [{container_device}]"
            )

        must_be_valid_path(host_device)
        must_be_valid_path(container_device)
        if cgroup_perm:
            must_be_valid_cgroup_perm(cgroup_perm)
        if not allow_disallowed:
            must_not_be_disallowed_device(hd)

        self.cgroup_perm: str = cgroup_perm
        self.host_device: str = hd
        self.container_device: str = cd

    def render(self):
        result = f"{self.host_device}:{self.container_device}"
        if self.cgroup_perm:
            result += f":{self.cgroup_perm}"
        return result


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

    def add_device(self, host_device: str, container_device: str, cgroup_perm: str = "", allow_disallowed=False):
        # Host device can be mapped to multiple container devices,
        # so we only make sure container devices are not duplicated
        if container_device in self._container_devices:
            raise RenderError(f"Device with container path [{container_device}] already added")

        self.devices.add(Device(host_device, container_device, cgroup_perm, allow_disallowed))
        self._container_devices.add(container_device)

    def has_devices(self):
        return len(self.devices) > 0

    def render(self) -> list[str]:
        return sorted([d.render() for d in self.devices])
