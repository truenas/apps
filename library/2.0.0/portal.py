try:
    from .error import RenderError
    from .validations import must_be_valid_portal_scheme, must_be_valid_path, must_be_valid_port
except ImportError:
    from error import RenderError
    from validations import must_be_valid_portal_scheme, must_be_valid_path, must_be_valid_port


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
        self._scheme = config.get("scheme", "http")
        self._host = config.get("host", "0.0.0.0")
        self._port = config.get("port", 0)
        self._path = config.get("path", "/")

        must_be_valid_portal_scheme(self._scheme)
        must_be_valid_path(self._path)
        must_be_valid_port(self._port)

    def render(self):
        return {
            "name": self._name,
            "scheme": self._scheme,
            "host": self._host,
            "port": self._port,
            "path": self._path,
        }
