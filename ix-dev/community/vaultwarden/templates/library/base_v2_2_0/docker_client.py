import docker
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from render import Render


class DockerClient:
    def __init__(self, render_instance: "Render"):
        self._render_instance = render_instance
        self._network_names: set[str] = set()

        try:
            self.client = docker.from_env()
        except Exception:
            self.client = None

        self._auto_fetch_networks()

    def _auto_fetch_networks(self):
        if self.client is None:
            return
        try:
            networks = self.client.networks.list()
        except Exception:
            pass

        for network in networks:
            if network.name is None:
                continue
            self._network_names.add(network.name)

    def network_exists(self, network_name: str) -> bool:
        return network_name in self._network_names
