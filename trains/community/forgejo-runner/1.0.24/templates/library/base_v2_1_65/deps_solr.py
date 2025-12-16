from typing import TYPE_CHECKING, TypedDict, NotRequired, List


if TYPE_CHECKING:
    from render import Render
    from storage import IxStorage


try:
    from .error import RenderError
    from .deps_perms import PermsContainer
except ImportError:
    from error import RenderError
    from deps_perms import PermsContainer


class SolrConfig(TypedDict):
    core: str
    modules: NotRequired[List[str]]
    port: NotRequired[int]
    volume: "IxStorage"


SUPPORTED_REPOS = ["solr"]


class SolrContainer:
    def __init__(
        self, render_instance: "Render", name: str, image: str, config: SolrConfig, perms_instance: PermsContainer
    ):
        self._render_instance = render_instance
        self._name = name
        self._config = config
        self._data_dir = "/var/solr"

        for key in ("core", "volume"):
            if key not in config:
                raise RenderError(f"Expected [{key}] to be set for solr")

        c = self._render_instance.add_container(name, image)

        user, group = 568, 568
        run_as = self._render_instance.values.get("run_as")
        if run_as:
            user = run_as["user"] or user  # Avoids running as root
            group = run_as["group"] or group  # Avoids running as root

        c.set_user(user, group)
        c.healthcheck.set_test("curl", {"port": self.get_port(), "path": f"/solr/{config['core']}/admin/ping"})
        c.remove_devices()
        c.add_storage(self._data_dir, config["volume"])

        c.set_command(["solr-precreate", config["core"]])

        c.environment.add_env("SOLR_PORT", self.get_port())
        if modules := config.get("modules"):
            c.environment.add_env("SOLR_MODULES", ",".join(modules))

        perms_instance.add_or_skip_action(
            f"{self._name}_solr_data", config["volume"], {"uid": user, "gid": group, "mode": "check"}
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
            raise RenderError(f"Unsupported repo [{repo}] for solr. Supported repos: {', '.join(SUPPORTED_REPOS)}")
        return repo

    def get_port(self):
        return self._config.get("port") or 8983

    def get_url(self):
        return f"http://{self._name}:{self.get_port()}/solr/{self._config['core']}"
