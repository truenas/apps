try:
    from .error import RenderError
    from .validations import must_be_valid_port, must_be_valid_port_protocol, must_be_valid_port_mode, must_be_valid_ip
except ImportError:
    from error import RenderError
    from validations import must_be_valid_port, must_be_valid_port_protocol, must_be_valid_port_mode, must_be_valid_ip


class Ports:
    def __init__(self, render_instance):
        self._render_instance = render_instance
        self._ports: dict[int, dict] = {}

    def add_port(self, host_port: int, container_port: int, config: dict | None = None):
        config = config or {}
        proto = config.get("protocol", "tcp")
        mode = config.get("mode", "ingress")
        host_ip = config.get("host_ip", "0.0.0.0")

        must_be_valid_port_protocol(proto)
        must_be_valid_port_mode(mode)
        must_be_valid_ip(host_ip)

        must_be_valid_port(host_port)
        must_be_valid_port(container_port)
        if host_port in self._ports.keys():
            raise RenderError(f"Host port [{host_port}] already added")
        self._ports[host_port] = {
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
