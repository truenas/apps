try:
    from .error import RenderError
    from .validations import valid_portal_scheme_or_raise, valid_path_or_raise, valid_port_or_raise
except ImportError:
    from error import RenderError
    from validations import valid_portal_scheme_or_raise, valid_path_or_raise, valid_port_or_raise


class Portals:
    def __init__(self, render_instance):
        self._render_instance = render_instance
        self._portals: set[Portal] = set()

    def add_portal(self, config: dict):
        name = config.get("name", "Web UI")

        if name in [p._name for p in self._portals]:
            raise RenderError(f"Portal [{name}] already added")

        self._portals.add(Portal(name, config))

    def render(self):
        return [p.render() for _, p in sorted([(p._name, p) for p in self._portals])]


class Portal:
    def __init__(self, name: str, config: dict):
        self._name = name
        self._scheme = valid_portal_scheme_or_raise(config.get("scheme", "http"))
        self._host = config.get("host", "0.0.0.0")
        self._port = valid_port_or_raise(config.get("port", 0))
        self._path = valid_path_or_raise(config.get("path", "/"))

    def render(self):
        return {
            "name": self._name,
            "scheme": self._scheme,
            "host": self._host,
            "port": self._port,
            "path": self._path,
        }
