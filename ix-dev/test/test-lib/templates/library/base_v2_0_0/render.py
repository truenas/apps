from .container import Container


class Render(object):
    def __init__(self, values):
        self.values = values
        self.containers = []
        self.volumes = []
        self.networks = []

    def add_container(self, name, image):
        container = Container(self, name, image)
        self.containers.append(container)
        return container

    def add_volume(self, volume):
        # TODO: Make sure no dupes are added.
        pass

    def render(self):
        services = {container.name: container.render() for container in self.containers}

        result = {"services": services}

        if self.volumes:
            result["volumes"] = {volume.name: volume.render() for volume in self.volumes}

        # if self.networks:
        #     result["networks"] = {...}

        return result
