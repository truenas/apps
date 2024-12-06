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


class MariadbConfig(TypedDict):
    user: str
    password: str
    database: str
    root_password: NotRequired[str]
    port: NotRequired[int]
    auto_upgrade: NotRequired[bool]
    volume: "IxStorage"


class MariadbContainer:
    def __init__(
        self, render_instance: "Render", name: str, image: str, config: MariadbConfig, perms_instance: PermsContainer
    ):
        self._render_instance = render_instance
        self._name = name

        for key in ("user", "password", "database", "volume"):
            if key not in config:
                raise RenderError(f"Expected [{key}] to be set for mariadb")

        port = valid_port_or_raise(config.get("port") or 3306)
        root_password = config.get("root_password") or config["password"]
        auto_upgrade = config.get("auto_upgrade", True)

        c = self._render_instance.add_container(name, image)
        c.set_user(999, 999)
        c.healthcheck.set_test("mariadb")
        c.remove_devices()

        c.add_storage("/var/lib/mysql", config["volume"])
        perms_instance.add_or_skip_action(
            f"{self._name}_mariadb_data", config["volume"], {"uid": 999, "gid": 999, "mode": "check"}
        )

        c.environment.add_env("MARIADB_USER", config["user"])
        c.environment.add_env("MARIADB_PASSWORD", config["password"])
        c.environment.add_env("MARIADB_ROOT_PASSWORD", root_password)
        c.environment.add_env("MARIADB_DATABASE", config["database"])
        c.environment.add_env("MARIADB_AUTO_UPGRADE", str(auto_upgrade).lower())
        c.set_command(["--port", str(port)])

        # Store container for further configuration
        # For example: c.depends.add_dependency("other_container", "service_started")
        self._container = c

    @property
    def container(self):
        return self._container
