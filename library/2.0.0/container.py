try:
    from .device import Device
    from .error import RenderError
    from .formatter import escape_dollar
    from .validations import (
        must_be_valid_network_mode,
        must_be_valid_restart_policy,
        must_be_valid_cap,
    )
except ImportError:
    from device import Device
    from error import RenderError
    from formatter import escape_dollar
    from validations import (
        must_be_valid_network_mode,
        must_be_valid_restart_policy,
        must_be_valid_cap,
    )


# from .storage import Storage


class Container:
    def __init__(self, render_instance, name: str, image: str):
        self.render_instance = render_instance
        # self.volume_mounts = []

        self.name: str = name
        self.image: str = self.resolve_image(image)
        self.user: str = ""
        self.tty: bool = False
        self.stdin_open: bool = False
        self.restart: str = "unless-stopped"
        # Drop all capabilities by default
        # If a CAP is needed it has to be added explicitly
        self.cap_drop: set[str] = set(["ALL"])
        self.cap_add: set[str] = set()
        self.security_opt: set[str] = set(["no-new-privileges"])
        self.network_mode: str = ""
        self.networks: set[str] = set()
        self.entrypoint: list[str] = []
        self.command: list[str] = []
        # TODO: automatically look for intel/amd devices now
        self.devices: set[Device] = set()

    # def add_volume(self, name, config):  # FIXME: define what "volume" is
    #     storage = Storage(self.render_instance, name, config)
    #     self.render_instance.add_volume(storage)
    #     self.volume_mounts.append(storage.volume_mount())

    def add_device(self, host_device: str, container_device: str):
        device = Device(host_device, container_device)
        # Host device can be mapped to multiple container devices,
        # so only make sure container devices are not duplicated
        if container_device in [d.container_device for d in self.devices]:
            raise RenderError(
                f"Device with container path [{container_device}] already added"
            )
        self.devices.add(device)

    def resolve_image(self, image: str):
        images = self.render_instance.values["images"]
        if image not in images:
            raise RenderError(f"Image [{image}] not found in values")
        repo = images[image].get("repository", "")
        tag = images[image].get("tag", "")

        if not repo:
            raise RenderError(f"Repository not found for image [{image}]")
        if not tag:
            raise RenderError(f"Tag not found for image [{image}]")

        return f"{repo}:{tag}"

    def set_user(self, user: int, group: int):
        for i in (user, group):
            if not isinstance(i, int) or i < 0:
                raise RenderError(f"User/Group [{i}] is not valid")
        self.user = f"{user}:{group}"

    def set_tty(self, enabled: bool = False):
        self.tty = enabled

    def set_stdin(self, enabled: bool = False):
        self.stdin_open = enabled

    def set_restart(self, policy: str):
        must_be_valid_restart_policy(policy)
        self.restart = policy

    def add_caps(self, caps: list[str]):
        for c in caps:
            if c in self.cap_add:
                raise RenderError(f"Capability [{c}] already added")
            must_be_valid_cap(c)
            self.cap_add.add(c)

    def add_security_opt(self, opt: str):
        if opt in self.security_opt:
            raise RenderError(f"Security Option [{opt}] already added")
        self.security_opt.add(opt)

    def remove_security_opt(self, opt: str):
        self.security_opt.remove(opt)

    def set_network_mode(self, mode: str):
        must_be_valid_network_mode(mode, self.render_instance.container_names())
        self.network_mode = mode

    def set_entrypoint(self, entrypoint: list[str]):
        self.entrypoint = [escape_dollar(e) for e in entrypoint]

    def set_command(self, command: list[str]):
        self.command = [escape_dollar(e) for e in command]

    def render(self):
        if self.network_mode and self.networks:
            raise RenderError("Cannot set both [network_mode] and [networks]")

        result = {
            "image": self.image,
            "tty": self.tty,
            "stdin_open": self.stdin_open,
            "restart": str(self.restart),
            "cap_drop": sorted(self.cap_drop),
        }

        if self.user:
            result["user"] = self.user

        if self.cap_add:
            result["cap_add"] = sorted(self.cap_add)

        if self.security_opt:
            result["security_opt"] = sorted(self.security_opt)

        if self.network_mode:
            result["network_mode"] = self.network_mode

        if self.entrypoint:
            result["entrypoint"] = self.entrypoint

        if self.command:
            result["command"] = self.command

        if self.devices:
            result["devices"] = [d.render() for d in self.devices]

        # if self.volume_mounts:
        #     result["volume_mounts"] = self.volume_mounts

        return result
