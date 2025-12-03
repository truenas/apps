import urllib.parse
from typing import TYPE_CHECKING, TypedDict, NotRequired

if TYPE_CHECKING:
    from render import Render
    from storage import IxStorage

try:
    from .error import RenderError
    from .deps_perms import PermsContainer
    from .validations import valid_port_or_raise, valid_redis_password_or_raise
except ImportError:
    from error import RenderError
    from deps_perms import PermsContainer
    from validations import valid_port_or_raise, valid_redis_password_or_raise


class RedisConfig(TypedDict):
    password: str
    port: NotRequired[int]
    volume: "IxStorage"


SUPPORTED_REPOS = ["redis", "valkey/valkey"]


class RedisContainer:
    def __init__(
        self, render_instance: "Render", name: str, image: str, config: RedisConfig, perms_instance: PermsContainer
    ):
        self._render_instance = render_instance
        self._name = name
        self._config = config

        for key in ("password", "volume"):
            if key not in config:
                raise RenderError(f"Expected [{key}] to be set for redis")

        valid_redis_password_or_raise(config["password"])

        port = valid_port_or_raise(self.get_port())
        self._get_repo(image)

        user, group = 568, 568
        run_as = self._render_instance.values.get("run_as")
        if run_as:
            user = run_as["user"] or user  # Avoids running as root
            group = run_as["group"] or group  # Avoids running as root
        c = self._render_instance.add_container(name, image)
        c.set_user(user, group)
        c.remove_devices()
        c.healthcheck.set_test("redis", {"password": config["password"]})

        cmd = []
        cmd.extend(["--port", str(port)])
        cmd.extend(["--requirepass", config["password"]])
        c.environment.add_env("REDIS_PASSWORD", config["password"])
        c.set_command(cmd)

        c.add_storage("/data", config["volume"])
        perms_instance.add_or_skip_action(
            f"{self._name}_redis_data", config["volume"], {"uid": user, "gid": group, "mode": "check"}
        )

        # Store container for further configuration
        # For example: c.depends.add_dependency("other_container", "service_started")
        self._container = c

    def _get_repo(self, image):
        images = self._render_instance.values["images"]
        if image not in images:
            raise RenderError(f"Image [{image}] not found in values. Available images: [{', '.join(images.keys())}]")
        repo = images[image].get("repository")
        if not repo:
            raise RenderError("Could not determine repo")
        if repo not in SUPPORTED_REPOS:
            raise RenderError(f"Unsupported repo [{repo}] for redis. Supported repos: {', '.join(SUPPORTED_REPOS)}")
        return repo

    def get_port(self):
        return self._config.get("port") or 6379

    def get_url(self, variant: str):
        addr = f"{self._name}:{self.get_port()}"
        password = urllib.parse.quote_plus(self._config["password"])

        match variant:
            case "redis":
                return f"redis://default:{password}@{addr}"

    @property
    def container(self):
        return self._container
