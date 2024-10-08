from typing import Any


try:
    from .depends import Depends
    from .deploy import Deploy
    from .device import Devices
    from .dns import Dns
    from .environment import Environment
    from .error import RenderError
    from .formatter import escape_dollar
    from .healthcheck import Healthcheck
    from .restart import RestartPolicy
    from .validations import must_be_valid_network_mode, must_be_valid_cap
except ImportError:
    from depends import Depends
    from deploy import Deploy
    from device import Devices
    from dns import Dns
    from environment import Environment
    from error import RenderError
    from formatter import escape_dollar
    from healthcheck import Healthcheck
    from restart import RestartPolicy
    from validations import must_be_valid_network_mode, must_be_valid_cap


# from .storage import Storage


class Container:
    def __init__(self, render_instance, name: str, image: str):
        self._render_instance = render_instance
        # self.volume_mounts = []

        self._name: str = name
        self._image: str = self._resolve_image(image)
        self._user: str = ""
        self._tty: bool = False
        self._stdin_open: bool = False
        # Drop all capabilities by default
        # If a CAP is needed it has to be added explicitly
        self._cap_drop: set[str] = set(["ALL"])
        self._cap_add: set[str] = set()
        self._security_opt: set[str] = set(["no-new-privileges"])
        self._network_mode: str = ""
        self._entrypoint: list[str] = []
        self._command: list[str] = []
        self._deploy: Deploy = Deploy(self._render_instance)
        self.networks: set[str] = set()
        self.devices: Devices = Devices(self._render_instance)
        self.environment: Environment = Environment(self._render_instance, self._deploy._resources)
        self.dns: Dns = Dns(self._render_instance)
        self.depends: Depends = Depends(self._render_instance)
        self.healthcheck: Healthcheck = Healthcheck(self._render_instance)
        self.restart: RestartPolicy = RestartPolicy(self._render_instance)

        # self.portals: set[Portal] = set()
        # self.notes: str = ""

    # def add_volume(self, name, config):  # FIXME: define what "volume" is
    #     storage = Storage(self.render_instance, name, config)
    #     self.render_instance.add_volume(storage)
    #     self.volume_mounts.append(storage.volume_mount())

    def _resolve_image(self, image: str):
        images = self._render_instance.values["images"]
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
        self._user = f"{user}:{group}"

    def set_tty(self, enabled: bool = False):
        self._tty = enabled

    def set_stdin(self, enabled: bool = False):
        self._stdin_open = enabled

    def add_caps(self, caps: list[str]):
        for c in caps:
            if c in self._cap_add:
                raise RenderError(f"Capability [{c}] already added")
            must_be_valid_cap(c)
            self._cap_add.add(c)

    def add_security_opt(self, opt: str):
        if opt in self._security_opt:
            raise RenderError(f"Security Option [{opt}] already added")
        self._security_opt.add(opt)

    def remove_security_opt(self, opt: str):
        self._security_opt.remove(opt)

    def set_network_mode(self, mode: str):
        must_be_valid_network_mode(mode, self._render_instance.container_names())
        self._network_mode = mode

    def set_entrypoint(self, entrypoint: list[str]):
        self._entrypoint = [escape_dollar(e) for e in entrypoint]

    def set_command(self, command: list[str]):
        self._command = [escape_dollar(e) for e in command]

    def render(self) -> dict[str, Any]:
        if self._network_mode and self.networks:
            raise RenderError("Cannot set both [network_mode] and [networks]")

        result = {
            "image": self._image,
            "tty": self._tty,
            "stdin_open": self._stdin_open,
            "restart": self.restart.render(),
            "cap_drop": sorted(self._cap_drop),
            "healthcheck": self.healthcheck.render(),
        }

        if self._user:
            result["user"] = self._user

        if self._cap_add:
            result["cap_add"] = sorted(self._cap_add)

        if self._security_opt:
            result["security_opt"] = sorted(self._security_opt)

        if self._network_mode:
            result["network_mode"] = self._network_mode

        if self._entrypoint:
            result["entrypoint"] = self._entrypoint

        if self._command:
            result["command"] = self._command

        if self.devices.has_devices():
            result["devices"] = self.devices.render()

        if self._deploy.has_deploy():
            result["deploy"] = self._deploy.render()

        if self.environment.has_variables():
            result["environment"] = self.environment.render()

        if self.dns.has_dns_nameservers():
            result["dns"] = self.dns.render_dns_nameservers()

        if self.dns.has_dns_searches():
            result["dns_search"] = self.dns.render_dns_searches()

        if self.dns.has_dns_opts():
            result["dns_opt"] = self.dns.render_dns_opts()

        if self.depends.has_dependencies():
            result["depends_on"] = self.depends.render()

        # if self.volume_mounts:
        #     result["volume_mounts"] = self.volume_mounts

        return result
