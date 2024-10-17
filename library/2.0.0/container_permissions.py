import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from render import Render


try:
    from .error import RenderError
    from .validations import valid_fs_path_or_raise
except ImportError:
    from error import RenderError
    from validations import valid_fs_path_or_raise


class ContainerPermissions:
    def __init__(self, render_instance: "Render"):
        self._render_instance = render_instance
        self._actions: dict[str, dict] = {}
        self._name = "ix-permissions"
        self._container = None

    def add_action(self, source: str, action: dict):
        # Generate the mount path here from the source,
        # this will ensure we don't have duplicate mount paths
        mount_path_key = self.normalize_source_for_path(source)

        if mount_path_key not in self._actions:
            self._actions[mount_path_key] = action
            if self._container is None:
                # On the first action added, setup the container
                # so other containers can depend on it
                self.setup_container()

        # If action is already added and this is called again.
        # Make sure the data is the same, otherwise raise an error
        for k, v in action.items():
            if self._actions[mount_path_key][k] != v:
                raise RenderError(
                    f"Permissions action [{mount_path_key}] was already added with [{k} = {v}], "
                    f"but now is [{k} = {self._actions[mount_path_key][k]}]"
                )

    def has_actions(self):
        return bool(self._actions)

    def setup_container(self):
        self._container = self._render_instance.add_container(self._name, "python_permissions_image")

        self._container.set_user(0, 0)
        self._container.add_caps(["CHOWN", "FOWNER", "DAC_OVERRIDE"])

        # Don't attach any devices
        self._container.deploy.resources.remove_devices()
        self._container.deploy.resources.set_profile("medium")
        self._container.restart.set_policy("on-failure", maximum_retry_count=0)
        self._container.healthcheck.disable()

        script = "#!/usr/bin/env python3\n"
        script += get_script()
        self._container.configs.add("permissions_run_script", script, "/script/run.py", "0700")
        self._container.set_entrypoint(["python3", "/script/run.py"])

    def normalize_source_for_path(self, source: str):
        return source.rstrip("/").lstrip("/").lower().replace("/", "_").replace(".", "-").replace(" ", "-")

    def finalize_container(self):
        assert self._container is not None

        actions_data: list[dict] = []
        for mount_path, action in self._actions.items():
            mount_path = f"/mnt/permissions/{mount_path}"
            self._container.add_storage(mount_path, action["config"])
            actions_data.append(
                {
                    "mount_path": valid_fs_path_or_raise(mount_path),
                    "source": action["source"],
                    "mode": action["mode"],
                    "uid": action["uid"],
                    "gid": action["gid"],
                    "chmod": action["chmod"],
                    "is_temporary": action["is_temporary"],
                }
            )

        actions_data_json = json.dumps(actions_data)
        self._container.configs.add("permissions_actions_data", actions_data_json, "/script/actions.json", "0500")


def get_script():
    return """
import os
import json
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
    print_chmod()

def fix_owner(path, uid, gid):
    print(f"Changing ownership to {uid}:{gid} on: [{path}]")
    os.chown(path, uid, gid)
    print("Ownership after changes:")
    print_chown()

def print_chown():
    curr_stat = os.stat(action["mount_path"])
    print(f"Ownership: [{curr_stat.st_uid}:{curr_stat.st_gid}]")

def print_chmod():
    curr_stat = os.stat(action["mount_path"])
    print(f"Permissions: [{oct(curr_stat.st_mode)[3:]}]")

def perform_action(action):
    print(f"=== Applying configuration on volume with source [{action['source']}] ===")

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
    print_chown()
    print_chmod()
    print("---")

    if action["mode"] == "always":
        fix_owner(action["mount_path"], action["uid"], action["gid"])
        if not action["chmod"]:
            print("Skipping permissions check, chmod is falsy")
        else:
            fix_perms(action["mount_path"], action["chmod"])
        return

    if action["mode"] == "check":
        curr_stat = os.stat(action["mount_path"])
        # no new line
        print(
            f"Ownership: wanted [{action['uid']}:{action['gid']}], "
            f"got [{curr_stat.st_uid}:{curr_stat.st_gid}].", end=" "
        )
        if curr_stat.st_uid != action["uid"] or curr_stat.st_gid != action["gid"]:
            print("Ownership is incorrect. Fixing...")
            fix_owner(action["mount_path"], action["uid"], action["gid"])
        else:
            print("Ownership is correct. Skipping...")

        if not action["chmod"]:
            print("Skipping permissions check, chmod is falsy")
        else:
            print(
                f"Permissions: wanted [{action['chmod']}], "
                f"got [{oct(curr_stat.st_mode)[3:]}].", end=" "
            )
            if oct(curr_stat.st_mode)[3:] != action["chmod"]:
                print("Permissions are incorrect. Fixing...")
                fix_perms(action["mount_path"], action["chmod"])
            else:
                print("Permissions are correct. Skipping...")

    print("=== Finished applying configuration on volume with source [{action['source']}] ===")
    print("")

if __name__ == "__main__":
    for action in actions_data:
        perform_action(action)
"""
