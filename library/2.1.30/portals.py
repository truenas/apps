from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from render import Render

try:
    from .error import RenderError
    from .portal import Portal
except ImportError:
    from error import RenderError
    from portal import Portal


class Portals:
    def __init__(self, render_instance: "Render"):
        self._render_instance = render_instance
        self._portals: set[Portal] = set()

    def add(self, port: dict, config: dict | None = None):
        config = config or {}
        name = config.get("name", "Web UI")
        host = config.get("host", None)

        host_ips = port.get("host_ips", [])
        if not isinstance(host_ips, list):
            raise RenderError("Expected [host_ips] to be a list of strings")

        # If host is not set, use the first host_ip (if it exists)
        if not host and len(host_ips) > 1:
            host = host_ips[0]

        config["host"] = host
        config["port"] = port.get("port_number", 0)

        if name in [p._name for p in self._portals]:
            raise RenderError(f"Portal [{name}] already added")
        self._portals.add(Portal(name, config))

    # FIXME: Remove this once all apps stop using it
    def add_portal(self, config: dict):
        name = config.get("name", "Web UI")

        if name in [p._name for p in self._portals]:
            raise RenderError(f"Portal [{name}] already added")

        self._portals.add(Portal(name, config))

    def render(self):
        return [p.render() for _, p in sorted([(p._name, p) for p in self._portals])]
