import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from render import Render


class ContainerPermissions:
    def __init__(self, render_instance: "Render"):
        self._render_instance = render_instance
        # TODO: check here if the permissions container is needed.
        # probably in the render_instance have a dict with the info needed.

    def add_container(self):
        c = self._render_instance.add_container("permissions", "python_permissions_image")

        c.set_user(0, 0)
        c.add_caps(["CHOWN", "FOWNER", "DAC_OVERRIDE"])

        # Don't attach any devices
        c.deploy.resources.remove_devices()
        c.deploy.resources.set_profile("medium")
        c.healthcheck.disable()

        # TODO: fill actions_data
        actions_data = {}
        actions_data = json.dumps(actions_data)
        script = """
        #!/usr/bin/env python3
        import os
        import json

        with open("/script/actions.json", "r") as f:
            actions_data = json.load(f)
        print(actions_data)

        # TODO:
        """

        c.configs.add("permissions_actions_data", actions_data, "/script/actions.json", "0500")
        c.configs.add("permissions_run_script", script, "/script/run.py", "0700")
        c.set_entrypoint(["python3", "/script/run.py"])

        # TODO: add volumes
