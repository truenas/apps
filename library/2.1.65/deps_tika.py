from typing import TYPE_CHECKING, TypedDict, NotRequired


if TYPE_CHECKING:
    from render import Render


try:
    from .error import RenderError
except ImportError:
    from error import RenderError


class TikaConfig(TypedDict):
    port: NotRequired[int]


SUPPORTED_REPOS = ["apache/tika"]


class TikaContainer:
    def __init__(self, render_instance: "Render", name: str, image: str, config: TikaConfig):
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
        c.healthcheck.set_test("wget", {"port": self.get_port(), "path": "/tika", "spider": False})
        c.remove_devices()

        c.set_command(["--port", str(self.get_port())])

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
        return self._config.get("port") or 9998

    def get_url(self):
        return f"http://{self._name}:{self.get_port()}"
