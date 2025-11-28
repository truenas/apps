from typing import TYPE_CHECKING, TypedDict, NotRequired


if TYPE_CHECKING:
    from render import Render
    from storage import IxStorage


try:
    from .error import RenderError
    from .deps_perms import PermsContainer
except ImportError:
    from error import RenderError
    from deps_perms import PermsContainer


class MeiliConfig(TypedDict):
    master_key: str
    port: NotRequired[int]
    volume: "IxStorage"


SUPPORTED_REPOS = ["getmeili/meilisearch"]


class MeilisearchContainer:
    def __init__(
        self, render_instance: "Render", name: str, image: str, config: MeiliConfig, perms_instance: PermsContainer
    ):
        self._render_instance = render_instance
        self._name = name
        self._config = config
        self._data_dir = "/meili_data"

        for key in ("master_key", "volume"):
            if key not in config:
                raise RenderError(f"Expected [{key}] to be set for meilisearch")

        c = self._render_instance.add_container(name, image)

        user, group = 568, 568
        run_as = self._render_instance.values.get("run_as")
        if run_as:
            user = run_as["user"] or user  # Avoids running as root
            group = run_as["group"] or group  # Avoids running as root

        c.set_user(user, group)
        c.healthcheck.set_test("curl", {"port": self.get_port(), "path": "/health"})
        c.remove_devices()
        c.add_storage(self._data_dir, config["volume"])

        c.environment.add_env("MEILI_HTTP_ADDR", f"0.0.0.0:{self.get_port()}")
        c.environment.add_env("MEILI_NO_ANALYTICS", True)
        c.environment.add_env("MEILI_EXPERIMENTAL_DUMPLESS_UPGRADE", True)
        c.environment.add_env("MEILI_MASTER_KEY", config["master_key"])

        perms_instance.add_or_skip_action(
            f"{self._name}_meili_data", config["volume"], {"uid": user, "gid": group, "mode": "check"}
        )

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
            raise RenderError(
                f"Unsupported repo [{repo}] for meilisearch. Supported repos: {', '.join(SUPPORTED_REPOS)}"
            )
        return repo

    def get_port(self):
        return self._config.get("port") or 7700

    def get_url(self):
        return f"http://{self._name}:{self.get_port()}"
