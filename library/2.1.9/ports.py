import ipaddress
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from render import Render

try:
    from .error import RenderError
    from .validations import (
        valid_ip_or_raise,
        valid_port_mode_or_raise,
        valid_port_or_raise,
        valid_port_protocol_or_raise,
    )
except ImportError:
    from error import RenderError
    from validations import (
        valid_ip_or_raise,
        valid_port_mode_or_raise,
        valid_port_or_raise,
        valid_port_protocol_or_raise,
    )


class Ports:
    def __init__(self, render_instance: "Render"):
        self._render_instance = render_instance
        self._ports: dict[str, dict] = {}

    def add_port(self, host_port: int, container_port: int, config: dict | None = None):
        config = config or {}
        host_port = valid_port_or_raise(host_port)
        container_port = valid_port_or_raise(container_port)
        proto = valid_port_protocol_or_raise(config.get("protocol", "tcp"))
        mode = valid_port_mode_or_raise(config.get("mode", "ingress"))

        # TODO: Once all apps stop using this function directly, (ie using the container.add_port function)
        # Remove this, and let container.add_port call this for each host_ip
        host_ip = config.get("host_ip", None)
        if host_ip is None:
            self.add_port(host_port, container_port, config | {"host_ip": "0.0.0.0"})
            self.add_port(host_port, container_port, config | {"host_ip": "::"})
            return

        host_ip = valid_ip_or_raise(config.get("host_ip", None))

        ip = ipaddress.ip_address(host_ip)
        ip_family = ip.version
        wildcard_ip = "0.0.0.0" if ip.version == 4 else "::"

        key = f"{host_port}_{host_ip}_{proto}_{ip_family}"
        if key in self._ports.keys():
            raise RenderError(f"Port [{host_port}/{proto}/ipv{ip_family}] already added for [{host_ip}]")

        if host_ip != wildcard_ip:
            # If the port we are adding is not going to use wildcard ip
            # Make sure that we don't have already added that port/proto to wildcard ip of the same family
            search_key = f"{host_port}_{wildcard_ip}_{proto}_{ip_family}"
            if search_key in self._ports.keys():
                raise RenderError(
                    f"Cannot bind port [{host_port}/{proto}/ipv{ip_family}] to [{host_ip}], "
                    f"already bound to [{wildcard_ip}]"
                )
        elif host_ip == wildcard_ip:
            # If the port we are adding is going to use wildcard ip
            # Make sure that we don't have already added that port/proto to a specific ip of the same family
            for p in self._ports.values():
                port_family = ipaddress.ip_address(p["host_ip"]).version
                if p["published"] == host_port and p["protocol"] == proto and port_family == ip_family:
                    raise RenderError(
                        f"Cannot bind port [{host_port}/{proto}/ipv{ip_family}] to [{host_ip}], "
                        f"already bound to [{p['host_ip']}]"
                    )

        self._ports[key] = {
            "published": host_port,
            "target": container_port,
            "protocol": proto,
            "mode": mode,
            "host_ip": host_ip,
        }

    def has_ports(self):
        return len(self._ports) > 0

    def render(self):
        ports = []
        wildcard_ports = {}

        # Ports that are not wildcards add them as is
        for key, p in self._ports.items():
            if p["host_ip"] not in ["0.0.0.0", "::"]:
                ports.append(p)
                continue

            wildcard_ports[key] = p

        # For wildcard ports, check if there is another wildcard port
        # in this case remove the host_ip field
        for wild_port in wildcard_ports.values():
            # Get the wildcard ip for the opposite family
            other_wildcard_ip = "0.0.0.0" if wild_port["host_ip"] == "::" else "::"
            # Make a copy of the port
            new_wild_port = wild_port.copy()

            # Check if there is another wildcard port with the opposite wildcard family
            if wild_port.copy() | {"host_ip": other_wildcard_ip} in wildcard_ports.values():
                new_wild_port.pop("host_ip")

            # Check that we haven't already added this port
            if new_wild_port not in ports:
                ports.append(new_wild_port)

        return sorted(ports, key=lambda p: f"{p['published']}_{p['published']}_{p['protocol']}_{p.get('host_ip', '_')}")
