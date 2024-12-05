try:
    from .validations import valid_portal_scheme_or_raise, valid_http_path_or_raise, valid_port_or_raise
except ImportError:
    from validations import valid_portal_scheme_or_raise, valid_http_path_or_raise, valid_port_or_raise


class Portal:
    def __init__(self, name: str, config: dict):
        self._name = name
        self._scheme = valid_portal_scheme_or_raise(config.get("scheme", "http"))
        self._host = config.get("host", "0.0.0.0") or "0.0.0.0"
        self._port = valid_port_or_raise(config.get("port", 0))
        self._path = valid_http_path_or_raise(config.get("path", "/"))

    def render(self):
        return {
            "name": self._name,
            "scheme": self._scheme,
            "host": self._host,
            "port": self._port,
            "path": self._path,
        }
