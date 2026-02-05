import docker
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from render import Render

try:
    from .error import RenderError
    from .validations import is_truenas_system
except ImportError:
    from error import RenderError
    from validations import is_truenas_system


class DockerClient:
    def __init__(self, render_instance: "Render"):
        self._render_instance = render_instance
        self._network_names: set[str] = set()

        try:
            self.client = docker.from_env()
        except Exception:
            if is_truenas_system():
                raise RenderError("Docker client could not be initialized.")
            self.client = None

        self._auto_fetch_networks()

    def _auto_fetch_networks(self):
        if self.client is None:
            return
        try:
            networks = self.client.networks.list()
        except Exception:
            if is_truenas_system():
                raise RenderError("Could not fetch networks from Docker client.")
            pass

        for network in networks:
            if network.name is None:
                continue
            self._network_names.add(network.name)

    def network_exists(self, network_name: str) -> bool:
        return True
        return network_name in self._network_names
