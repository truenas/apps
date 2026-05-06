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


class ElasticConfig(TypedDict):
    password: str
    node_name: str
    port: NotRequired[int]
    volume: "IxStorage"


SUPPORTED_REPOS = ["elasticsearch"]


class ElasticSearchContainer:
    def __init__(
        self, render_instance: "Render", name: str, image: str, config: ElasticConfig, perms_instance: PermsContainer
    ):
        self._render_instance = render_instance
        self._name = name
        self._config = config
        self._data_dir = "/usr/share/elasticsearch/data"

        for key in ("password", "node_name", "volume"):
            if key not in config:
                raise RenderError(f"Expected [{key}] to be set for ElasticSearch")

        c = self._render_instance.add_container(name, image)

        c.set_user(1000, 1000)
        basic_auth_header = self._render_instance.funcs["basic_auth_header"]("elastic", config["password"])
        c.healthcheck.set_test(
            "curl",
            {
                "port": self.get_port(),
                "path": "/_cluster/health?local=true",
                "headers": [("Authorization", basic_auth_header)],
            },
        )
        c.remove_devices()
        c.add_storage(self._data_dir, config["volume"])

        c.environment.add_env("ELASTIC_PASSWORD", config["password"])
        c.environment.add_env("http.port", self.get_port())
        c.environment.add_env("path.data", self._data_dir)
        c.environment.add_env("path.repo", self.get_snapshots_dir())
        c.environment.add_env("node.name", config["node_name"])
        c.environment.add_env("discovery.type", "single-node")
        c.environment.add_env("xpack.security.enabled", True)
        c.environment.add_env("xpack.security.transport.ssl.enabled", False)

        perms_instance.add_or_skip_action(
            f"{self._name}_elastic_data", config["volume"], {"uid": 1000, "gid": 1000, "mode": "check"}
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
                f"Unsupported repo [{repo}] for elastic search. Supported repos: {', '.join(SUPPORTED_REPOS)}"
            )
        return repo

    def get_port(self):
        return self._config.get("port") or 9200

    def get_url(self):
        return f"http://{self._name}:{self.get_port()}"

    def get_snapshots_dir(self):
        return f"{self._data_dir}/snapshots"
