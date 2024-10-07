try:
    from error import RenderError
    from container import Container
except ImportError:
    from .error import RenderError
    from .container import Container


class Render(object):
    def __init__(self, values):
        self.values: dict = values
        self.containers: dict[str, Container] = {}
        # self.volumes = {}
        # self.networks = {}

    def container_names(self):
        return self.containers.keys()

    def add_container(self, name: str, image: str):
        container = Container(self, name, image)
        if name in self.containers:
            raise RenderError(f"Container {name} already exists.")
        self.containers[name] = container
        return container

    # def add_volume(self, volume):
    #     # TODO: Make sure no dupes are added.
    #     pass

    def render(self):
        result: dict = {}

        if not self.containers:
            raise RenderError("No containers added.")

        services = {c.name: c.render() for c in self.containers.values()}
        result["services"] = services

        # if self.volumes:
        #     result["volumes"] = {volume.name: volume.render() for volume in self.volumes.values()}

        # if self.networks:
        #     result["networks"] = {...}

        return result
