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
    "timescale/timescaledb",
    "ghcr.io/immich-app/postgres",
]
SUPPORTED_UPGRADE_REPOS = [
    "postgres",
    "postgis/postgis",
    "pgvector/pgvector",
    # "timescale/timescaledb", // Currently NOT supported for upgrades
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
        # 0.8.1-pg17-trixie
        regex = re.compile(r"^\d+\.\d+\.\d+\-pg\d+(\-\w+)?")

        def oper(x):
            parts = x.split("-")
            return parts[1].lstrip("pg")

    elif variant == "ghcr.io/immich-app/postgres":
        # 15-vectorchord0.4.3
        regex = re.compile(r"^\d+\-vectorchord\d+\.\d+\.\d+")

        def oper(x):
            return x.split("-")[0]

    elif variant == "timescale/timescaledb":
        # 2.24.0-pg18
        regex = re.compile(r"^\d+\.\d+\.\d+-pg\d+")

        def oper(x):
            parts = x.split("-")
            return parts[1].lstrip("pg")

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
        self._data_dir = None
        self._upgrade_name = f"{self._name}_upgrade"
        self._upgrade_container = None

        for key in ("user", "password", "database", "volume"):
            if key not in config:
                raise RenderError(f"Expected [{key}] to be set for postgres")

        port = valid_port_or_raise(self.get_port())

        # TODO: Set some defaults for ZFS Optimizations (Need to check if applies on updates)
        # https://vadosware.io/post/everything-ive-seen-on-optimizing-postgres-on-zfs-on-linux/

        opts = []
        for k, v in config.get("additional_options", {}).items():
            opts.extend(["-c", f"{k}={v}"])

        common_variables = {
            "POSTGRES_USER": config["user"],
            "POSTGRES_PASSWORD": config["password"],
            "POSTGRES_DB": config["database"],
            "PGPORT": port,
        }

        c = self._render_instance.add_container(name, image)
        c.healthcheck.set_test("postgres", {"user": config["user"], "db": config["database"], "port": port})
        c.set_shm_size_mb(256)

        if opts:
            c.set_command(opts)

        containers = [c]

        # eg we don't want to handle upgrades of pg_vector or immich at the moment
        repo = self._get_repo(image)
        if repo in SUPPORTED_UPGRADE_REPOS:
            self._data_dir = "/var/lib/postgresql"
            target_major_version = self._get_target_version(image)
            # This is the new format upstream Postgres uses/suggests.
            # E.g., for Postgres 17, the data dir is /var/lib/postgresql/17/docker
            common_variables.update({"PGDATA": f"{self._data_dir}/{target_major_version}/docker"})

            upg = self._render_instance.add_container(self._upgrade_name, "postgres_upgrade_image")

            self._upgrade_container = upg
            containers.append(upg)

            upg.set_entrypoint(["/bin/bash", "-c", "/upgrade.sh"])
            upg.restart.set_policy("on-failure", 1)
            upg.healthcheck.disable()
            upg.setup_as_helper(profile="medium")
            upg.environment.add_env("TARGET_VERSION", target_major_version)

            c.depends.add_dependency(self._upgrade_name, "service_completed_successfully")
        else:
            self._data_dir = "/var/lib/postgresql/data"

        for container in containers:
            # TODO: We can now use 568:568 (or any user/group).
            # Need to first plan a migration path for the existing users.
            container.set_user(999, 999)
            container.remove_devices()
            container.add_storage(self._data_dir, config["volume"])
            for k, v in common_variables.items():
                container.environment.add_env(k, v)

        perms_instance.add_or_skip_action(
            f"{self._name}_postgres_data", config["volume"], {"uid": 999, "gid": 999, "mode": "check"}
        )

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
