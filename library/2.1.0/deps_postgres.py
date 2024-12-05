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


class PostgresContainer:
    def __init__(
        self, render_instance: "Render", name: str, image: str, config: PostgresConfig, perms_instance: PermsContainer
    ):
        self._render_instance = render_instance
        self._name = name
        self._config = config

        for key in ("user", "password", "database", "volume"):
            if key not in config:
                raise RenderError(f"Expected [{key}] to be set for postgres")

        port = valid_port_or_raise(self._get_port())

        c = self._render_instance.add_container(name, image)
        c.set_user(999, 999)
        c.healthcheck.set_test("postgres")
        c.remove_devices()

        c.add_storage("/var/lib/postgresql/data", config["volume"])
        perms_instance.add_or_skip_action(
            f"{self._name}_postgres_data", config["volume"], {"uid": 999, "gid": 999, "mode": "check"}
        )

        c.environment.add_env("POSTGRES_USER", config["user"])
        c.environment.add_env("POSTGRES_PASSWORD", config["password"])
        c.environment.add_env("POSTGRES_DB", config["database"])
        c.environment.add_env("POSTGRES_PORT", port)

        # Store container for further configuration
        # For example: c.depends.add_dependency("other_container", "service_started")
        self._container = c

    @property
    def container(self):
        return self._container

    def _get_port(self):
        return self._config.get("port") or 5432

    def get_url(self, variant: str):
        user = urllib.parse.quote_plus(self._config["user"])
        password = urllib.parse.quote_plus(self._config["password"])
        creds = f"{user}:{password}"
        addr = f"{self._name}:{self._get_port()}"
        db = self._config["database"]

        match variant:
            case "postgres":
                return f"postgres://{creds}@{addr}/{db}?sslmode=disable"
            case "postgresql":
                return f"postgresql://{creds}@{addr}/{db}?sslmode=disable"
            case "postgresql_no_creds":
                return f"postgresql://{addr}/{db}?sslmode=disable"
            case "host_port":
                return addr
            case _:
                raise RenderError(f"Expected [variant] to be one of [postgres, postgresql], got [{variant}]")
