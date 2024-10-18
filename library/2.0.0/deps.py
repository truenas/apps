from typing import TYPE_CHECKING, TypedDict, NotRequired

if TYPE_CHECKING:
    from render import Render

try:
    from .error import RenderError
    from .validations import valid_port_or_raise
except ImportError:
    from error import RenderError
    from validations import valid_port_or_raise


class PostgresConfig(TypedDict):
    user: str
    password: str
    database: str
    port: NotRequired[int]
    volume: dict  # TODO: Define a type for this, its used in many places


class MariadbConfig(TypedDict):
    user: str
    password: str
    database: str
    root_password: NotRequired[str]
    port: NotRequired[int]
    auto_upgrade: NotRequired[bool]
    volume: dict  # TODO: Define a type for this, its used in many places


class RedisConfig(TypedDict):
    password: str
    port: NotRequired[int]
    volume: dict  # TODO: Define a type for this, its used in many places


class Deps:
    def __init__(self, render_instance: "Render"):
        self._render_instance = render_instance

    def postgres(self, name: str, image: str, config: PostgresConfig):
        for key in ("user", "password", "database", "volume"):
            if key not in config:
                raise RenderError(f"Expected [{key}] to be set for postgres")

        port = valid_port_or_raise(config.get("port") or 5432)

        c = self._render_instance.add_container(name, image)
        c.set_user(999, 999)
        c.healthcheck.set_test("postgres")
        c.deploy.resources.remove_devices()

        c.add_storage("/var/lib/postgresql/data", config["volume"], {"uid": 999, "gid": 999, "mode": "check"})

        c.environment.add_env("POSTGRES_USER", config["user"])
        c.environment.add_env("POSTGRES_PASSWORD", config["password"])
        c.environment.add_env("POSTGRES_DB", config["database"])
        c.environment.add_env("POSTGRES_PORT", port)

        # Return container for further configuration
        # For example: c.depends.add_dependency("other_container", "service_started")
        return c

    def redis(self, name: str, image: str, config: RedisConfig):
        for key in ("password", "volume"):
            if key not in config:
                raise RenderError(f"Expected [{key}] to be set for redis")

        port = valid_port_or_raise(config.get("port") or 6379)

        c = self._render_instance.add_container(name, image)
        c.set_user(1001, 0)
        c.healthcheck.set_test("redis")
        c.deploy.resources.remove_devices()

        c.add_storage("/bitnami/redis/data", config["volume"], {"uid": 1001, "gid": 0, "mode": "check"})

        c.environment.add_env("ALLOW_EMPTY_PASSWORD", "no")
        c.environment.add_env("REDIS_PASSWORD", config["password"])
        c.environment.add_env("REDIS_PORT_NUMBER", port)

        # Return container for further configuration
        # For example: c.depends.add_dependency("other_container", "service_started")
        return c

    def mariadb(self, name: str, image: str, config: MariadbConfig):
        for key in ("user", "password", "database", "volume"):
            if key not in config:
                raise RenderError(f"Expected [{key}] to be set for mariadb")

        port = valid_port_or_raise(config.get("port") or 3306)
        root_password = config.get("root_password") or config["password"]
        auto_upgrade = config.get("auto_upgrade", True)

        c = self._render_instance.add_container(name, image)
        c.set_user(999, 999)
        c.healthcheck.set_test("mariadb")
        c.deploy.resources.remove_devices()

        c.add_storage("/var/lib/mysql", config["volume"], {"uid": 999, "gid": 999, "mode": "check"})

        c.environment.add_env("MARIADB_USER", config["user"])
        c.environment.add_env("MARIADB_PASSWORD", config["password"])
        c.environment.add_env("MARIADB_ROOT_PASSWORD", root_password)
        c.environment.add_env("MARIADB_DATABASE", config["database"])
        c.environment.add_env("MARIADB_AUTO_UPGRADE", str(auto_upgrade).lower())
        c.set_command(["--port", str(port)])
