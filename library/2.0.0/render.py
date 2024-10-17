import copy

try:
    from .container import Container
    from .container_permissions import ContainerPermissions
    from .configs import Configs
    from .error import RenderError
    from .functions import Functions
    from .notes import Notes
    from .portals import Portals
    from .volumes import Volumes
except ImportError:
    from container import Container
    from container_permissions import ContainerPermissions
    from configs import Configs
    from error import RenderError
    from functions import Functions
    from notes import Notes
    from portals import Portals
    from volumes import Volumes


class Render(object):
    def __init__(self, values):
        self._containers: dict[str, Container] = {}
        self.values = values
        self._add_images_internal_use()
        # Make a copy after we inject the images
        self._original_values: dict = copy.deepcopy(self.values)

        self._permissions_container: ContainerPermissions = ContainerPermissions(self)

        self.configs = Configs(render_instance=self)
        self.funcs = Functions(render_instance=self).func_map()
        self.portals: Portals = Portals(render_instance=self)
        self.notes: Notes = Notes(render_instance=self)
        self.volumes = Volumes(render_instance=self)

    def _add_images_internal_use(self):
        if not self.values.get("images"):
            self.values["images"] = {}

        if "python_permissions_image" not in self.values["images"]:
            self.values["images"]["python_permissions_image"] = {"repository": "python", "tag": "3.13.0-slim-bookworm"}

    def has_permissions_actions(self):
        return self._permissions_container.has_actions()

    def permissions_container_name(self):
        return self._permissions_container._name

    def container_names(self):
        return list(self._containers.keys())

    def add_container(self, name: str, image: str):
        container = Container(self, name, image)
        if name in self._containers:
            raise RenderError(f"Container {name} already exists.")
        self._containers[name] = container
        return container

    def render(self):
        if self.values != self._original_values:
            raise RenderError("Values have been modified since the renderer was created.")

        if self.has_permissions_actions():
            self._permissions_container.finalize_container()

        if not self._containers:
            raise RenderError("No containers added.")

        result: dict = {
            "x-notes": self.notes.render(),
            "x-portals": self.portals.render(),
            "services": {c._name: c.render() for c in self._containers.values()},
        }

        if self.volumes.has_volumes():
            result["volumes"] = self.volumes.render()

        if self.configs.has_configs():
            result["configs"] = self.configs.render()

        # if self.networks:
        #     result["networks"] = {...}

        return result
