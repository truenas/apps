from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from render import Render

try:
    from .error import RenderError
    from .labels import Labels
except ImportError:
    from error import RenderError
    from labels import Labels


class Networks:
    def __init__(self, render_instance: "Render"):
        self._render_instance = render_instance
        self._networks: dict[str, Network] = {}

    def create_internal(self, name: str) -> str:
        """Creates an internal network. Only used for internal communication between containers."""
        name = "ix-internal-" + name

        if self.exists(name):
            raise RenderError(f"Network [{name}] already exists.")

        net_config = {
            "external": False,
            "enable_ipv4": True,
            # We disable IPv6 for internal networks, because there is an upstream bug,
            # which any ipv6 network takes priority over ipv4 networks even with gw_priority set.
            # https://github.com/moby/moby/issues/51999
            "enable_ipv6": False,
            "labels": {"ix.internal": "true"},
        }

        self._networks[name] = Network(name, net_config)
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

        # We only need to define the network as external,
        # the lifecycle of the network is managed outside of the renderer,
        # via the Docker CLI or other tools.
        self._networks[name] = Network(name, {"external": True})

    def has_items(self):
        return bool(self._networks)

    def exists(self, name: str):
        return name in self._networks

    def render(self):
        result: dict = {}
        for name in sorted(self._networks.keys()):
            result[name] = self._networks[name].render()
        return result


@dataclass
class NetworkConfig:
    name: str | None = None
    """If set, this name will be used instead of the generated name."""
    external: bool | None = None
    """If true, this network is managed externally."""
    enable_ipv6: bool | None = None
    """If true, this network will have IPv6 enabled."""
    enable_ipv4: bool | None = None
    """If true, this network will have IPv4 enabled."""
    labels: Labels | None = None
    """If set, this will be added as labels to the network."""

    def __post_init__(self):
        if isinstance(self.labels, dict):
            labels_dict = self.labels
            self.labels = Labels()
            for key, value in labels_dict.items():
                self.labels.add_label(key, value)

        if self.enable_ipv4 is not None and self.enable_ipv6 is not None:
            # If both explicitly set to false, we should error out
            if not self.enable_ipv4 and not self.enable_ipv6:
                raise RenderError(f"Network [{self.name}] cannot have both IPv4 and IPv6 disabled")


class Network:
    def __init__(self, name: str, config: dict = {}):
        self._name = name
        self._config = NetworkConfig(**config)

    def render(self):
        result: dict = {}
        if self._config.name is not None:
            result["name"] = self._config.name
        if self._config.external is not None:
            result["external"] = self._config.external
        if self._config.enable_ipv4 is not None:
            result["enable_ipv4"] = self._config.enable_ipv4
        if self._config.enable_ipv6 is not None:
            result["enable_ipv6"] = self._config.enable_ipv6
        if self._config.labels and self._config.labels.has_labels():
            result["labels"] = self._config.labels.render()

        return result


@dataclass
class ContainerNetworkConfig:
    interface_name: str | None = None
    """If set, this will be the name of the network interface inside the container."""
    mac_address: str | None = None
    """If set, this will be the MAC address of the network interface inside the container."""
    ipv4_address: str | None = None
    """If set, this will be the IPv4 address of the network interface inside the container."""
    ipv6_address: str | None = None
    """If set, this will be the IPv6 address of the network interface inside the container."""
    gw_priority: int | None = None
    """The network with the highest gw_priority is selected as the default gateway for the service container."""
    priority: int | None = None
    """Indicates in which order Compose connects the service’s containers to its networks."""


class ContainerNetworks:
    def __init__(self, render_instance: "Render"):
        self._render_instance = render_instance
        self._networks: dict[str, ContainerNetwork] = {}

    def add(self, container_name: str, net_name: str, config: dict = {}):
        if not self._render_instance.networks.exists(net_name):
            raise RenderError(
                f"Network [{net_name}] must be first registered. "
                "This is probably a bug in the renderer, please report it."
            )

        if self.exists(net_name):
            raise RenderError(f"Network [{net_name}] already added to the container [{container_name}].")

        net = ContainerNetwork(net_name, config)
        for existing_net in self._networks.values():
            if net._config.interface_name and existing_net._config.interface_name:
                if net._config.interface_name == existing_net._config.interface_name:
                    raise RenderError(
                        f"Network [{net_name}] cannot have the same interface name "
                        f"[{net._config.interface_name}] as network [{existing_net._name}]"
                        f" in container [{container_name}]"
                    )
            if net._config.mac_address and existing_net._config.mac_address:
                if net._config.mac_address == existing_net._config.mac_address:
                    raise RenderError(
                        f"Network [{net_name}] cannot have the same MAC address "
                        f"[{net._config.mac_address}] as network [{existing_net._name}]"
                        f" in container [{container_name}]"
                    )
            if net._config.ipv4_address and existing_net._config.ipv4_address:
                if net._config.ipv4_address == existing_net._config.ipv4_address:
                    raise RenderError(
                        f"Network [{net_name}] cannot have the same IPv4 address "
                        f"[{net._config.ipv4_address}] as network [{existing_net._name}]"
                        f" in container [{container_name}]"
                    )
            if net._config.ipv6_address and existing_net._config.ipv6_address:
                if net._config.ipv6_address == existing_net._config.ipv6_address:
                    raise RenderError(
                        f"Network [{net_name}] cannot have the same IPv6 address "
                        f"[{net._config.ipv6_address}] as network [{existing_net._name}]"
                        f" in container [{container_name}]"
                    )
            if isinstance(net._config.gw_priority, int) and isinstance(existing_net._config.gw_priority, int):
                if net._config.gw_priority == existing_net._config.gw_priority:
                    raise RenderError(
                        f"Network [{net_name}] cannot have the same gateway priority "
                        f"[{net._config.gw_priority}] as network [{existing_net._name}]"
                        f" in container [{container_name}]"
                    )
            if isinstance(net._config.priority, int) and isinstance(existing_net._config.priority, int):
                if net._config.priority == existing_net._config.priority:
                    raise RenderError(
                        f"Network [{net_name}] cannot have the same priority "
                        f"[{net._config.priority}] as network [{existing_net._name}]"
                        f" in container [{container_name}]"
                    )

        self._networks[net_name] = net

    def has_items(self):
        return bool(self._networks)

    def exists(self, name: str):
        return name in self._networks

    def render(self):
        result: dict = {}
        for name in sorted(self._networks.keys()):
            result[name] = self._networks[name].render()
        return result


class ContainerNetwork:
    def __init__(self, name: str, config: dict = {}):
        self._name = name
        self._config = ContainerNetworkConfig(**config)

    def render(self):
        result: dict = {}
        if self._config.interface_name:
            result["interface_name"] = self._config.interface_name
        if self._config.ipv4_address:
            result["ipv4_address"] = self._config.ipv4_address
        if self._config.ipv6_address:
            result["ipv6_address"] = self._config.ipv6_address
        if self._config.mac_address:
            result["mac_address"] = self._config.mac_address
        if isinstance(self._config.gw_priority, int):
            result["gw_priority"] = self._config.gw_priority
        if isinstance(self._config.priority, int):
            result["priority"] = self._config.priority
        return result
