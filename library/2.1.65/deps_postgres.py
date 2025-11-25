import re
import urllib.parse
from typing import TYPE_CHECKING, TypedDict, NotRequired


if TYPE_CHECKING:
    from render import Render
    from storage import IxStorage


try:
    from .error import RenderError
    from .deps_perms import PermsContainer
    from .validations import valid_port_or_raise
except ImportError:
    from error import RenderError
    from deps_perms import PermsContainer
    from validations import valid_port_or_raise


class PostgresConfig(TypedDict):
    user: str
    password: str
    database: str
    port: NotRequired[int]
    volume: "IxStorage"
    additional_options: NotRequired[dict[str, str]]


MAX_POSTGRES_VERSION = 18
SUPPORTED_REPOS = [
    "postgres",
    "postgis/postgis",
    "pgvector/pgvector",
    "ghcr.io/immich-app/postgres",
]


def get_major_version(variant: str, tag: str):
    if variant == "postgres":
        # 17.7-bookworm
        regex = re.compile(r"^\d+\.\d+-\w+")

        def oper(x):
            return x.split(".")[0]

    elif variant == "postgis/postgis":
        # 17-3.5
        regex = re.compile(r"^\d+\-\d+\.\d+")

        def oper(x):
            return x.split("-")[0]

    elif variant == "pgvector/pgvector":
        # 0.8.1-pg17
        regex = re.compile(r"^\d+\.\d+\.\d+\-pg\d+")

        def oper(x):
            return x.split("-")[1].lstrip("pg")

    elif variant == "ghcr.io/immich-app/postgres":
        # 15-vectorchord0.4.3-pgvectors0.2.0
        regex = re.compile(r"^\d+\-vectorchord\d+\.\d+\.\d+(\-pgvectors?\d+\.\d+\.\d+)?")

        def oper(x):
            return x.split("-")[0]

    if not regex.match(tag):
        raise RenderError(f"Could not determine major version from tag [{tag}] for variant [{variant}]")

    return oper(tag)


class PostgresContainer:
    def __init__(
        self, render_instance: "Render", name: str, image: str, config: PostgresConfig, perms_instance: PermsContainer
    ):
        self._render_instance = render_instance
        self._name = name
        self._config = config
        self._data_dir = "/var/lib/postgresql/data"
        self._upgrade_name = f"{self._name}_upgrade"
        self._upgrade_container = None

        for key in ("user", "password", "database", "volume"):
            if key not in config:
                raise RenderError(f"Expected [{key}] to be set for postgres")

        port = valid_port_or_raise(self.get_port())

        c = self._render_instance.add_container(name, image)

        c.set_user(999, 999)
        c.healthcheck.set_test("postgres", {"user": config["user"], "db": config["database"]})
        c.set_shm_size_mb(256)
        c.remove_devices()
        c.add_storage(self._data_dir, config["volume"])

        perms_instance.add_or_skip_action(
            f"{self._name}_postgres_data", config["volume"], {"uid": 999, "gid": 999, "mode": "check"}
        )

        opts = []
        for k, v in config.get("additional_options", {}).items():
            opts.extend(["-c", f"{k}={v}"])
        if opts:
            c.set_command(opts)

        common_variables = {
            "POSTGRES_USER": config["user"],
            "POSTGRES_PASSWORD": config["password"],
            "POSTGRES_DB": config["database"],
            "PGPORT": port,
            "PGDATA": self._data_dir,
        }

        # eg we don't want to handle upgrades of pg_vector or immich at the moment
        repo = self._get_repo(image)
        if repo == "postgres":
            target_major_version = self._get_target_version(image)
            # We force this data directory here, because from 18 onwards,
            # The default data directory defaults to /var/lib/postgresql/MAJOR_VERSION/docker
            # This makes it hard for the upgrade container to find the data directory
            # Having a fixed data directory makes it easier to manage across versions
            # Drawback is that we can't take advantage of the "fast" upgrades using `--link`.
            # Later on we might want to revisit this decision and migrate to the new data structure
            common_variables["PGDATA"] = self._data_dir
            if target_major_version >= 18:
                # Before 18, the default was no data checksums.
                # We need to keep it that way so it is compatible for upgrades.
                # Also it is recommended to have this disabled as ZFS does its own check-summing.
                common_variables["POSTGRES_INITDB_ARGS"] = "--no-data-checksums"

            upg = self._render_instance.add_container(self._upgrade_name, "postgres_upgrade_image")
            upg.set_entrypoint(["/bin/bash", "-c", "/upgrade.sh"])
            upg.restart.set_policy("on-failure", 1)
            upg.set_user(999, 999)
            upg.healthcheck.disable()
            upg.remove_devices()
            upg.add_storage(self._data_dir, config["volume"])
            for k, v in common_variables.items():
                upg.environment.add_env(k, v)

            upg.environment.add_env("TARGET_VERSION", target_major_version)
            upg.environment.add_env("DATA_DIR", self._data_dir)

            self._upgrade_container = upg

            c.depends.add_dependency(self._upgrade_name, "service_completed_successfully")

        for k, v in common_variables.items():
            c.environment.add_env(k, v)

        # Store container for further configuration
        # For example: c.depends.add_dependency("other_container", "service_started")
        self._container = c

    @property
    def container(self):
        return self._container

    def add_dependency(self, container_name: str, condition: str):
        self._container.depends.add_dependency(container_name, condition)
        if self._upgrade_container:
            self._upgrade_container.depends.add_dependency(container_name, condition)

    def _get_repo(self, image):
        images = self._render_instance.values["images"]
        if image not in images:
            raise RenderError(f"Image [{image}] not found in values. Available images: [{', '.join(images.keys())}]")
        repo = images[image].get("repository")
        if not repo:
            raise RenderError("Could not determine repo")
        if repo not in SUPPORTED_REPOS:
            raise RenderError(f"Unsupported repo [{repo}] for postgres. Supported repos: {', '.join(SUPPORTED_REPOS)}")
        return repo

    def _get_target_version(self, image):
        repo = self._get_repo(image)
        images = self._render_instance.values["images"]
        if image not in images:
            raise RenderError(f"Image [{image}] not found in values. Available images: [{', '.join(images.keys())}]")
        tag = str(images[image].get("tag", ""))
        target_major_version = get_major_version(repo, tag)

        try:
            # Make sure we end up with an integer
            target_major_version = int(target_major_version)
        except ValueError:
            raise RenderError(f"Could not determine target major version from tag [{tag}]")

        if target_major_version > MAX_POSTGRES_VERSION:
            raise RenderError(f"Postgres version [{target_major_version}] is not supported")

        return target_major_version

    def get_port(self):
        return self._config.get("port") or 5432

    def get_url(self, variant: str):
        user = urllib.parse.quote_plus(self._config["user"])
        password = urllib.parse.quote_plus(self._config["password"])
        creds = f"{user}:{password}"
        addr = f"{self._name}:{self.get_port()}"
        db = self._config["database"]

        urls = {
            "postgres": f"postgres://{creds}@{addr}/{db}?sslmode=disable",
            "postgresql": f"postgresql://{creds}@{addr}/{db}?sslmode=disable",
            "postgresql_no_creds": f"postgresql://{addr}/{db}?sslmode=disable",
            "jdbc": f"jdbc:postgresql://{addr}/{db}",
            "host_port": addr,
        }

        if variant not in urls:
            raise RenderError(f"Expected [variant] to be one of [{', '.join(urls.keys())}], got [{variant}]")
        return urls[variant]
