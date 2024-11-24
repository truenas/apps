from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from render import Render
    from storage import IxStorage

try:
    from .configs import ContainerConfigs
    from .depends import Depends
    from .deploy import Deploy
    from .devices import Devices
    from .dns import Dns
    from .environment import Environment
    from .error import RenderError
    from .formatter import escape_dollar, get_image_with_hashed_data
    from .healthcheck import Healthcheck
    from .labels import Labels
    from .ports import Ports
    from .restart import RestartPolicy
    from .validations import valid_network_mode_or_raise, valid_cap_or_raise
    from .storage import Storage
except ImportError:
    from configs import ContainerConfigs
    from depends import Depends
    from deploy import Deploy
    from devices import Devices
    from dns import Dns
    from environment import Environment
    from error import RenderError
    from formatter import escape_dollar, get_image_with_hashed_data
    from healthcheck import Healthcheck
    from labels import Labels
    from ports import Ports
    from restart import RestartPolicy
    from validations import valid_network_mode_or_raise, valid_cap_or_raise
    from storage import Storage


class Container:
    def __init__(self, render_instance: "Render", name: str, image: str):
        self._render_instance = render_instance

        self._name: str = name
        self._image: str = self._resolve_image(image)
        self._build_image: str = ""
        self._user: str = ""
        self._tty: bool = False
        self._stdin_open: bool = False
        self._init: bool | None = None
        self._read_only: bool | None = None
        self._hostname: str = ""
        self._cap_drop: set[str] = set(["ALL"])  # Drop all capabilities by default and add caps granularly
        self._cap_add: set[str] = set()
        self._security_opt: set[str] = set(["no-new-privileges"])
        self._group_add: set[int | str] = set()
        self._network_mode: str = ""
        self._entrypoint: list[str] = []
        self._command: list[str] = []
        self._grace_period: int | None = None
        self._shm_size: int | None = None
        self._storage: Storage = Storage(self._render_instance)
        self.configs: ContainerConfigs = ContainerConfigs(self._render_instance, self._render_instance.configs)
        self.deploy: Deploy = Deploy(self._render_instance)
        self.networks: set[str] = set()
        self.devices: Devices = Devices(self._render_instance)
        self.environment: Environment = Environment(self._render_instance, self.deploy.resources)
        self.dns: Dns = Dns(self._render_instance)
        self.depends: Depends = Depends(self._render_instance)
        self.healthcheck: Healthcheck = Healthcheck(self._render_instance)
        self.labels: Labels = Labels(self._render_instance)
        self.restart: RestartPolicy = RestartPolicy(self._render_instance)
        self.ports: Ports = Ports(self._render_instance)

        self._auto_set_network_mode()
        self._auto_add_labels()
        self._auto_add_groups()

    def _auto_add_groups(self):
        self.add_group(568)

    def _auto_set_network_mode(self):
        if self._render_instance.values.get("network", {}).get("host_network", False):
            self.set_network_mode("host")

    def _auto_add_labels(self):
        labels = self._render_instance.values.get("labels", [])
        if not labels:
            return

        for label in labels:
            containers = label.get("containers", [])
            if not containers:
                raise RenderError(f'Label [{label.get("key", "")}] must have at least one container')

            if self._name in containers:
                self.labels.add_label(label["key"], label["value"])

    def _resolve_image(self, image: str):
        images = self._render_instance.values["images"]
        if image not in images:
            raise RenderError(
                f"Image [{image}] not found in values. " f"Available images: [{', '.join(images.keys())}]"
            )
        repo = images[image].get("repository", "")
        tag = images[image].get("tag", "")

        if not repo:
            raise RenderError(f"Repository not found for image [{image}]")
        if not tag:
            raise RenderError(f"Tag not found for image [{image}]")

        return f"{repo}:{tag}"

    def build_image(self, content: list[str | None]):
        dockerfile = f"FROM {self._image}\n"
        for line in content:
            if not line:
                continue
            if line.startswith("FROM"):
                # TODO: This will also block multi-stage builds
                # We can revisit this later if we need it
                raise RenderError(
                    "FROM cannot be used in build image. Define the base image when creating the container."
                )
            dockerfile += line + "\n"

        self._build_image = dockerfile
        self._image = get_image_with_hashed_data(self._image, dockerfile)

    def set_user(self, user: int, group: int):
        for i in (user, group):
            if not isinstance(i, int) or i < 0:
                raise RenderError(f"User/Group [{i}] is not valid")
        self._user = f"{user}:{group}"

    def add_group(self, group: int | str):
        if isinstance(group, str):
            group = str(group).strip()
            if group.isdigit():
                raise RenderError(f"Group is a number [{group}] but passed as a string")

        if group in self._group_add:
            raise RenderError(f"Group [{group}] already added")
        self._group_add.add(group)

    def get_current_groups(self) -> list[str]:
        return [str(g) for g in self._group_add]

    def set_tty(self, enabled: bool = False):
        self._tty = enabled

    def set_stdin(self, enabled: bool = False):
        self._stdin_open = enabled

    def set_init(self, enabled: bool = False):
        self._init = enabled

    def set_read_only(self, enabled: bool = False):
        self._read_only = enabled

    def set_hostname(self, hostname: str):
        self._hostname = hostname

    def set_grace_period(self, grace_period: int):
        if grace_period < 0:
            raise RenderError(f"Grace period [{grace_period}] cannot be negative")
        self._grace_period = grace_period

    def add_caps(self, caps: list[str]):
        for c in caps:
            if c in self._cap_add:
                raise RenderError(f"Capability [{c}] already added")
            self._cap_add.add(valid_cap_or_raise(c))

    def add_security_opt(self, opt: str):
        if opt in self._security_opt:
            raise RenderError(f"Security Option [{opt}] already added")
        self._security_opt.add(opt)

    def remove_security_opt(self, opt: str):
        self._security_opt.remove(opt)

    def set_network_mode(self, mode: str):
        self._network_mode = valid_network_mode_or_raise(mode, self._render_instance.container_names())

    def set_entrypoint(self, entrypoint: list[str]):
        self._entrypoint = [escape_dollar(e) for e in entrypoint]

    def set_command(self, command: list[str]):
        self._command = [escape_dollar(e) for e in command]

    def add_storage(self, mount_path: str, config: "IxStorage"):
        self._storage.add(mount_path, config)

    def set_shm_size_mb(self, size: int):
        self._shm_size = size

    # Easily remove devices from the container
    # Useful in dependencies like postgres and redis
    # where there is no need to pass devices to them
    def remove_devices(self):
        self.deploy.resources.remove_devices()
        self.devices.remove_devices()

    @property
    def storage(self):
        return self._storage

    def render(self) -> dict[str, Any]:
        if self._network_mode and self.networks:
            raise RenderError("Cannot set both [network_mode] and [networks]")

        result = {
            "image": self._image,
            "platform": "linux/amd64",
            "tty": self._tty,
            "stdin_open": self._stdin_open,
            "restart": self.restart.render(),
            "cap_drop": sorted(self._cap_drop),
            "healthcheck": self.healthcheck.render(),
        }

        if self._hostname:
            result["hostname"] = self._hostname

        if self._build_image:
            result["build"] = {"tags": [self._image], "dockerfile_inline": self._build_image}

        if self.configs.has_configs():
            result["configs"] = self.configs.render()

        if self._init is not None:
            result["init"] = self._init

        if self._read_only is not None:
            result["read_only"] = self._read_only

        if self._grace_period is not None:
            result["stop_grace_period"] = self._grace_period

        if self._user:
            result["user"] = self._user

        if self.deploy.resources.has_gpus() or self.devices.has_devices():
            self.add_group(44)  # video
            self.add_group(107)  # render

        if self._group_add:
            result["group_add"] = sorted(self._group_add, key=lambda g: (isinstance(g, str), g))

        if self._shm_size is not None:
            result["shm_size"] = f"{self._shm_size}M"

        if self._cap_add:
            result["cap_add"] = sorted(self._cap_add)

        if self._security_opt:
            result["security_opt"] = sorted(self._security_opt)

        if self._network_mode:
            result["network_mode"] = self._network_mode

        if self._network_mode != "host":
            if self.ports.has_ports():
                result["ports"] = self.ports.render()

        if self._entrypoint:
            result["entrypoint"] = self._entrypoint

        if self._command:
            result["command"] = self._command

        if self.devices.has_devices():
            result["devices"] = self.devices.render()

        if self.deploy.has_deploy():
            result["deploy"] = self.deploy.render()

        if self.environment.has_variables():
            result["environment"] = self.environment.render()

        if self.labels.has_labels():
            result["labels"] = self.labels.render()

        if self.dns.has_dns_nameservers():
            result["dns"] = self.dns.render_dns_nameservers()

        if self.dns.has_dns_searches():
            result["dns_search"] = self.dns.render_dns_searches()

        if self.dns.has_dns_opts():
            result["dns_opt"] = self.dns.render_dns_opts()

        if self.depends.has_dependencies():
            result["depends_on"] = self.depends.render()

        if self._storage.has_mounts():
            result["volumes"] = self._storage.render()

        return result
