from typing import TYPE_CHECKING, TypedDict, NotRequired


if TYPE_CHECKING:
    from render import Render


try:
    from .error import RenderError
except ImportError:
    from error import RenderError


class MemcachedConfig(TypedDict):
    port: NotRequired[int]
    memory_mb: NotRequired[int]


SUPPORTED_REPOS = ["memcached"]


class MemcachedContainer:

    def __init__(self, render_instance: "Render", name: str, image: str, config: MemcachedConfig):
        self._render_instance = render_instance
        self._name = name
        self._config = config

        c = self._render_instance.add_container(name, image)

        user, group = 568, 568
        run_as = self._render_instance.values.get("run_as")
        if run_as:
            user = run_as["user"] or user  # Avoids running as root
            group = run_as["group"] or group  # Avoids running as root

        c.set_user(user, group)
        c.healthcheck.set_test("tcp", {"port": self.get_port()})
        c.remove_devices()
        c.set_grace_period(60)

        mem = self._config.get("memory_mb") or 256
        c.set_command(["-p", str(self.get_port()), "-m", f"{mem}M"])

        self._get_repo(image)

        # Store container for further configuration
        # For example: c.depends.add_dependency("other_container", "service_started")
        self._container = c

    @property
    def container(self):
        return self._container

    def _get_repo(self, image):
        images = self._render_instance.values["images"]
        if image not in images:
            raise RenderError(f"Image [{image}] not found in values. Available images: [{', '.join(images.keys())}]")
        repo = images[image].get("repository")
        if not repo:
            raise RenderError("Could not determine repo")
        if repo not in SUPPORTED_REPOS:
            raise RenderError(f"Unsupported repo [{repo}] for tika. Supported repos: {', '.join(SUPPORTED_REPOS)}")
        return repo

    def get_port(self):
        return self._config.get("port") or 11211
