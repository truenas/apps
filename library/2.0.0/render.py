import copy

try:
    from .container import Container
    from .error import RenderError
    from .functions import Functions
    from .notes import Notes
    from .portal import Portals
    from .volumes import Volumes
except ImportError:
    from container import Container
    from error import RenderError
    from functions import Functions
    from notes import Notes
    from portal import Portals
    from volumes import Volumes


class Render(object):
    def __init__(self, values):
        self._original_values: dict = values
        self._containers: dict[str, Container] = {}
        self.values: dict = copy.deepcopy(values)

        self.funcs = Functions(render_instance=self).func_map()
        self.portals: Portals = Portals(render_instance=self)
        self.notes: Notes = Notes(render_instance=self)
        self.volumes = Volumes(render_instance=self)

        # self.networks = {}

    def container_names(self):
        return list(self._containers.keys())

    def add_container(self, name: str, image: str):
        container = Container(self, self.volumes, name, image)
        if name in self._containers:
            raise RenderError(f"Container {name} already exists.")
        self._containers[name] = container
        return container

    def render(self):
        if self.values != self._original_values:
            raise RenderError("Values have been modified since the renderer was created.")

        if not self._containers:
            raise RenderError("No containers added.")

        result: dict = {
            "x-notes": self.notes.render(),
            "x-portals": self.portals.render(),
            "services": {c._name: c.render() for c in self._containers.values()},
        }

        if self.volumes.has_volumes():
            result["volumes"] = self.volumes.render()

        # if self.networks:
        #     result["networks"] = {...}

        return result
