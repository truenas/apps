from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from render import Render

try:
    from .error import RenderError
    from .validations import (
        valid_port_or_raise,
        valid_port_protocol_or_raise,
        valid_port_mode_or_raise,
        valid_ip_or_raise,
    )
except ImportError:
    from error import RenderError
    from validations import (
        valid_port_or_raise,
        valid_port_protocol_or_raise,
        valid_port_mode_or_raise,
        valid_ip_or_raise,
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
        host_ip = valid_ip_or_raise(config.get("host_ip", "0.0.0.0"))

        key = f"{host_port}_{host_ip}_{proto}"
        if key in self._ports.keys():
            raise RenderError(f"Port [{host_port}/{proto}] already added for [{host_ip}]")

        if host_ip != "0.0.0.0":
            # If the port we are adding is not going to use 0.0.0.0
            # Make sure that we don't have already added that port/proto to 0.0.0.0
            search_key = f"{host_port}_0.0.0.0_{proto}"
            if search_key in self._ports.keys():
                raise RenderError(f"Cannot bind port [{host_port}/{proto}] to [{host_ip}], already bound to [0.0.0.0]")
        elif host_ip == "0.0.0.0":
            # If the port we are adding is going to use 0.0.0.0
            # Make sure that we don't have already added that port/proto to a specific ip
            for p in self._ports.values():
                if p["published"] == host_port and p["protocol"] == proto:
                    raise RenderError(
                        f"Cannot bind port [{host_port}/{proto}] to [{host_ip}], already bound to [{p['host_ip']}]"
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
        return [config for _, config in sorted(self._ports.items())]
