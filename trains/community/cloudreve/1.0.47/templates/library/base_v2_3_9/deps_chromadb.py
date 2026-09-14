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


class ChromaConfig(TypedDict):
    port: NotRequired[int]
    volume: "IxStorage"


SUPPORTED_REPOS = ["ghcr.io/chroma-core/chroma"]


class ChromaContainer:
    def __init__(
        self, render_instance: "Render", name: str, image: str, config: ChromaConfig, perms_instance: PermsContainer
    ):
        self._render_instance = render_instance
        self._name = name
        self._config = config
        self._data_dir = "/data"

        for key in ("volume",):
            if key not in config:
                raise RenderError(f"Expected [{key}] to be set for chromadb")

        c = self._render_instance.add_container(name, image)

        user, group = 568, 568
        run_as = self._render_instance.values.get("run_as")
        if run_as:
            user = run_as["user"] or user  # Avoids running as root
            group = run_as["group"] or group  # Avoids running as root

        c.set_user(user, group)
        c.healthcheck.set_test("http", {"port": self.get_port(), "path": "/api/v2/healthcheck"})
        c.remove_devices()
        c.set_grace_period(60)
        c.add_storage(self._data_dir, config["volume"])

        c.environment.add_env("CHROMA_PERSIST_PATH", self._data_dir)
        c.environment.add_env("CHROMA_LISTEN_ADDRESS", "0.0.0.0")
        c.environment.add_env("CHROMA_PORT", self.get_port())

        perms_instance.add_or_skip_action(
            f"{self._name}_chromadb_data", config["volume"], {"uid": user, "gid": group, "mode": "check"}
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
            raise RenderError(f"Unsupported repo [{repo}] for chromadb. Supported repos: {', '.join(SUPPORTED_REPOS)}")
        return repo

    def get_port(self):
        return self._config.get("port") or 8000
