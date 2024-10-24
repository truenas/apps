import os
import json
from typing import TYPE_CHECKING, TypedDict, NotRequired

if TYPE_CHECKING:
    from render import Render
    from storage import IxStorage

try:
    from .error import RenderError
    from .validations import valid_port_or_raise, valid_fs_path_or_raise, valid_octal_mode_or_raise
except ImportError:
    from error import RenderError
    from validations import valid_port_or_raise, valid_fs_path_or_raise, valid_octal_mode_or_raise


class PostgresConfig(TypedDict):
    user: str
    password: str
    database: str
    port: NotRequired[int]
    volume: "IxStorage"


class MariadbConfig(TypedDict):
    user: str
    password: str
    database: str
    root_password: NotRequired[str]
    port: NotRequired[int]
    auto_upgrade: NotRequired[bool]
    volume: "IxStorage"


class RedisConfig(TypedDict):
    password: str
    port: NotRequired[int]
    volume: "IxStorage"


class PermsContainer:
    def __init__(self, render_instance: "Render", name: str):
        self._render_instance = render_instance
        self._name = name
        self.actions: set[str] = set()
        self.parsed_configs: list[dict] = []

    def add_or_skip_action(self, identifier: str, volume_config: "IxStorage", action_config: dict):
        identifier = self.normalize_identifier_for_path(identifier)
        if identifier in self.actions:
            raise RenderError(f"Action with id [{identifier}] already used for another permission action")

        parsed_action = self.parse_action(identifier, volume_config, action_config)
        if parsed_action:
            self.parsed_configs.append(parsed_action)
            self.actions.add(identifier)

    def parse_action(self, identifier: str, volume_config: "IxStorage", action_config: dict):
        valid_modes = ["always", "check"]
        mode = action_config.get("mode", "check")
        uid = action_config.get("uid", None)
        gid = action_config.get("gid", None)
        chmod = action_config.get("chmod", None)
        mount_path = os.path.join("/mnt/permission", identifier)

        auto_perms = volume_config.get("auto_permissions", False)
        is_temporary = False
        # If it is a temporary volume, we force auto permissions
        # and set is_temporary to True, so it will be cleaned up
        if volume_config.get("type", "") == "temporary":
            is_temporary = True
            auto_perms = True

        # Skip ACL enabled volumes
        if volume_config.get("ix_volume_config", {}).get("acl_enable", False):
            return None
        if volume_config.get("host_path_config", {}).get("acl_enable", False):
            return None

        # On ix_volumes, we set auto permissions with "check" mode
        if volume_config.get("ix_volume_config", {}):
            auto_perms = True
            mode = "check"

        # Skip volumes that do not have auto permissions set
        if not auto_perms:
            return None

        if mode not in valid_modes:
            raise RenderError(f"Expected [mode] to be one of [{', '.join(valid_modes)}], got [{mode}]")
        if not isinstance(uid, int) or not isinstance(gid, int):
            raise RenderError("Expected [uid] and [gid] to be set when [auto_permissions] is enabled")
        if chmod is not None:
            chmod = valid_octal_mode_or_raise(chmod)

        mount_path = valid_fs_path_or_raise(mount_path)
        return {
            "mount_path": mount_path,
            "volume_config": volume_config,
            "action_data": {
                "mount_path": mount_path,
                "is_temporary": is_temporary,
                "identifier": identifier,
                "mode": mode,
                "uid": uid,
                "gid": gid,
                "chmod": chmod,
            },
        }

    def normalize_identifier_for_path(self, identifier: str):
        return identifier.rstrip("/").lstrip("/").lower().replace("/", "_").replace(".", "-").replace(" ", "-")

    def has_actions(self):
        return bool(self.actions)

    def activate(self):
        if len(self.parsed_configs) != len(self.actions):
            raise RenderError("Number of actions and parsed configs does not match")

        if not self.has_actions():
            raise RenderError("No actions added. Check if there are actions before activating")

        # Add the container and set it up
        c = self._render_instance.add_container(self._name, "python_permissions_image")
        c.set_user(0, 0)
        c.add_caps(["CHOWN", "FOWNER", "DAC_OVERRIDE"])

        # Don't attach any devices
        c.deploy.resources.remove_devices()
        c.deploy.resources.set_profile("medium")
        c.restart.set_policy("on-failure", maximum_retry_count=0)
        c.healthcheck.disable()

        c.set_entrypoint(["python3", "/script/run.py"])
        script = "#!/usr/bin/env python3\n"
        script += get_script()
        c.configs.add("permissions_run_script", script, "/script/run.py", "0700")

        actions_data: list[dict] = []
        for parsed in self.parsed_configs:
            c.add_storage(parsed["mount_path"], parsed["volume_config"])
            actions_data.append(parsed["action_data"])

        actions_data_json = json.dumps(actions_data)
        c.configs.add("permissions_actions_data", actions_data_json, "/script/actions.json", "0500")


def get_script():
    return """
import os
import json
import time
import shutil

with open("/script/actions.json", "r") as f:
    actions_data = json.load(f)

if not actions_data:
    # If this script is called, there should be actions data
    raise ValueError("No actions data found")

def fix_perms(path, chmod):
    print(f"Changing permissions to {chmod} on: [{path}]")
    os.chmod(path, int(chmod, 8))
    print("Permissions after changes:")
    print_chmod_stat()

def fix_owner(path, uid, gid):
    print(f"Changing ownership to {uid}:{gid} on: [{path}]")
    os.chown(path, uid, gid)
    print("Ownership after changes:")
    print_chown_stat()

def print_chown_stat():
    curr_stat = os.stat(action["mount_path"])
    print(f"Ownership: [{curr_stat.st_uid}:{curr_stat.st_gid}]")

def print_chmod_stat():
    curr_stat = os.stat(action["mount_path"])
    print(f"Permissions: [{oct(curr_stat.st_mode)[3:]}]")

def print_chown_diff(curr_stat, uid, gid):
    print(f"Ownership: wanted [{uid}:{gid}], got [{curr_stat.st_uid}:{curr_stat.st_gid}].")

def print_chmod_diff(curr_stat, mode):
    print(f"Permissions: wanted [{mode}], got [{oct(curr_stat.st_mode)[3:]}].")

def perform_action(action):
    start_time = time.time()
    print(f"=== Applying configuration on volume with identifier [{action['identifier']}] ===")

    if not os.path.isdir(action["mount_path"]):
        print(f"Path [{action['mount_path']}] is not a directory, skipping...")
        return

    if action["is_temporary"]:
        print(f"Path [{action['mount_path']}] is a temporary directory, ensuring it is empty...")
        for item in os.listdir(action["mount_path"]):
            item_path = os.path.join(action["mount_path"], item)

            # Exclude the safe directory, where we can use to mount files temporarily
            if os.path.basename(item_path) == "ix-safe":
                continue
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)

    if not action["is_temporary"] and os.listdir(action["mount_path"]):
        print(f"Path [{action['mount_path']}] is not empty, skipping...")
        return

    print(f"Current Ownership and Permissions on [{action['mount_path']}]:")
    curr_stat = os.stat(action["mount_path"])
    print_chown_diff(curr_stat, action["uid"], action["gid"])
    print_chmod_diff(curr_stat, action["chmod"])
    print("---")

    if action["mode"] == "always":
        fix_owner(action["mount_path"], action["uid"], action["gid"])
        if not action["chmod"]:
            print("Skipping permissions check, chmod is falsy")
        else:
            fix_perms(action["mount_path"], action["chmod"])
        return

    elif action["mode"] == "check":
        if curr_stat.st_uid != action["uid"] or curr_stat.st_gid != action["gid"]:
            print("Ownership is incorrect. Fixing...")
            fix_owner(action["mount_path"], action["uid"], action["gid"])
        else:
            print("Ownership is correct. Skipping...")

        if not action["chmod"]:
            print("Skipping permissions check, chmod is falsy")
        else:
            if oct(curr_stat.st_mode)[3:] != action["chmod"]:
                print("Permissions are incorrect. Fixing...")
                fix_perms(action["mount_path"], action["chmod"])
            else:
                print("Permissions are correct. Skipping...")

    print(f"Time taken: {(time.time() - start_time) * 1000:.2f}ms")
    print(f"=== Finished applying configuration on volume with identifier [{action['identifier']}] ===")

if __name__ == "__main__":
    start_time = time.time()
    for action in actions_data:
        perform_action(action)
    print(f"Total time taken: {(time.time() - start_time) * 1000:.2f}ms")
"""


class Deps:
    def __init__(self, render_instance: "Render"):
        self._render_instance = render_instance

    def perms(self, name: str):
        return PermsContainer(self._render_instance, name)

    def postgres(self, name: str, image: str, config: PostgresConfig, perms_instance: PermsContainer):
        for key in ("user", "password", "database", "volume"):
            if key not in config:
                raise RenderError(f"Expected [{key}] to be set for postgres")

        port = valid_port_or_raise(config.get("port") or 5432)

        c = self._render_instance.add_container(name, image)
        c.set_user(999, 999)
        c.healthcheck.set_test("postgres")
        c.deploy.resources.remove_devices()

        c.add_storage("/var/lib/postgresql/data", config["volume"])
        perms_instance.add_or_skip_action("postgres_data", config["volume"], {"uid": 999, "gid": 999, "mode": "check"})

        c.environment.add_env("POSTGRES_USER", config["user"])
        c.environment.add_env("POSTGRES_PASSWORD", config["password"])
        c.environment.add_env("POSTGRES_DB", config["database"])
        c.environment.add_env("POSTGRES_PORT", port)

        # Return container for further configuration
        # For example: c.depends.add_dependency("other_container", "service_started")
        return c

    def redis(self, name: str, image: str, config: RedisConfig, perms_instance: PermsContainer):
        for key in ("password", "volume"):
            if key not in config:
                raise RenderError(f"Expected [{key}] to be set for redis")

        port = valid_port_or_raise(config.get("port") or 6379)

        c = self._render_instance.add_container(name, image)
        c.set_user(1001, 0)
        c.healthcheck.set_test("redis")
        c.deploy.resources.remove_devices()

        c.add_storage("/bitnami/redis/data", config["volume"])
        perms_instance.add_or_skip_action("redis_data", config["volume"], {"uid": 1001, "gid": 0, "mode": "check"})

        c.environment.add_env("ALLOW_EMPTY_PASSWORD", "no")
        c.environment.add_env("REDIS_PASSWORD", config["password"])
        c.environment.add_env("REDIS_PORT_NUMBER", port)

        # Return container for further configuration
        # For example: c.depends.add_dependency("other_container", "service_started")
        return c

    def mariadb(self, name: str, image: str, config: MariadbConfig, perms_instance: PermsContainer):
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

        c.add_storage("/var/lib/mysql", config["volume"])
        perms_instance.add_or_skip_action("mariadb_data", config["volume"], {"uid": 999, "gid": 999, "mode": "check"})

        c.environment.add_env("MARIADB_USER", config["user"])
        c.environment.add_env("MARIADB_PASSWORD", config["password"])
        c.environment.add_env("MARIADB_ROOT_PASSWORD", root_password)
        c.environment.add_env("MARIADB_DATABASE", config["database"])
        c.environment.add_env("MARIADB_AUTO_UPGRADE", str(auto_upgrade).lower())
        c.set_command(["--port", str(port)])

        # Return container for further configuration
        # For example: c.depends.add_dependency("other_container", "service_started")
        return c
