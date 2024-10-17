import json
import inspect
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
        script += inspect.getsource(_permissions_script)
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
                    "mode": action["mode"],
                    "uid": action["uid"],
                    "gid": action["gid"],
                    "chmod": action["chmod"],
                    "is_temporary": action["is_temporary"],
                }
            )

        actions_data_json = json.dumps(actions_data)
        self._container.configs.add("permissions_actions_data", actions_data_json, "/script/actions.json", "0500")


def _permissions_script():
    import json

    # TODO:

    with open("/script/actions.json", "r") as f:
        actions_data = json.load(f)
    print(actions_data)
