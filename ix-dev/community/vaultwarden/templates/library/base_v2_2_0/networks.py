from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from render import Render

try:
    from .error import RenderError
except ImportError:
    from error import RenderError


class Networks:
    def __init__(self, render_instance: "Render"):
        self._render_instance = render_instance
        self._networks: dict[str, Network] = {}

    def create_internal(self, name: str) -> str:
        """Creates an internal network. Only used for internal communication between containers."""
        name = "ix-internal-" + name

        if self.exists(name):
            raise RenderError(f"Network [{name}] already exists.")
        self._networks[name] = Network(
            name,
            {
                "internal": False,
                "attachable": False,
                "external": False,
            },
        )
        return name

    def register(self, name: str):
        """
        Adds a top level network. Network must already exist, for example created via Docker CLI.
        This is used to reference external networks that are not managed by the renderer.
        """
        if not self._render_instance.docker.network_exists(name):
            raise RenderError(f"Network [{name}] has to be created before it can be used. ie via Docker CLI")

        if self.exists(name):
            raise RenderError(f"Network [{name}] already exists.")
        self._networks[name] = Network(
            name,
            {
                "internal": False,
                "attachable": False,
                "external": True,
            },
        )

    def has_items(self):
        return len(self._networks) > 0

    def exists(self, name: str):
        return name in self._networks

    def render(self):
        result: dict = {}
        for name, network in sorted([(n._name, n) for n in self._networks.values()]):
            result[name] = network.render()
        return result


@dataclass
class NetworkConfig:
    name: str | None = None
    """If set, this name will be used instead of the generated name."""
    internal: bool = False
    """If true, this network will be internal and not have access to external networks, including the 'internet'."""
    external: bool = False
    """If true, this network is managed externally."""
    attachable: bool = False
    """If true, standalone containers can join the network."""


class Network:
    def __init__(self, name: str, config: dict):
        self._name = name
        self._config = NetworkConfig(**config)

    def render(self):
        result: dict = {
            "external": self._config.external,
            "internal": self._config.internal,
            "attachable": self._config.attachable,
        }

        if self._config.name is not None:
            result["name"] = self._config.name

        return result


@dataclass
class ContainerNetworkConfig:
    # Nothing yet
    pass


class ContainerNetworks:
    def __init__(self, render_instance: "Render"):
        self._render_instance = render_instance
        self._networks: dict[str, ContainerNetwork] = {}

    def add(self, name: str, config: dict = {}):
        if not self._render_instance.networks.exists(name):
            raise RenderError(
                f"Network [{name}] must be first registered. This is probably a bug in the renderer, please report it."
            )

        if self.exists(name):
            raise RenderError(f"Network [{name}] already added to the container.")

        self._networks[name] = ContainerNetwork(name, config)

    def has_items(self):
        return len(self._networks) > 0

    def exists(self, name: str):
        return name in self._networks

    def render(self):
        result: dict = {}
        for name, network in sorted([(n._name, n) for n in self._networks.values()]):
            result[name] = network.render()
        return result


class ContainerNetwork:
    def __init__(self, name: str, config: dict = {}):
        self._name = name
        self._config = ContainerNetworkConfig(**config)

    def render(self):
        return {}
