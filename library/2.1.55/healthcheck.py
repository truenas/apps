import json
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from render import Render

try:
    from .error import RenderError
    from .formatter import escape_dollar
    from .validations import valid_http_path_or_raise
except ImportError:
    from error import RenderError
    from formatter import escape_dollar
    from validations import valid_http_path_or_raise


class Healthcheck:
    def __init__(self, render_instance: "Render"):
        self._render_instance = render_instance
        self._test: str | list[str] = ""
        self._interval_sec: int = 30
        self._timeout_sec: int = 5
        self._retries: int = 5
        self._start_period_sec: int = 15
        self._start_interval_sec: int = 2
        self._disabled: bool = False
        self._use_built_in: bool = False

    def _get_test(self):
        if isinstance(self._test, str):
            return escape_dollar(self._test)
        return [escape_dollar(t) for t in self._test]

    def disable(self):
        self._disabled = True

    def use_built_in(self):
        self._use_built_in = True

    def set_custom_test(self, test: str | list[str]):
        if isinstance(test, list):
            if test[0] == "CMD" and any(t.startswith("$") for t in test):
                raise RenderError(f"Healthcheck with 'CMD' cannot contain shell variables '{test}'")
        if self._disabled:
            raise RenderError("Cannot set custom test when healthcheck is disabled")
        self._test = test

    def set_test(self, variant: str, config: dict | None = None):
        config = config or {}
        self.set_custom_test(test_mapping(variant, config))

    def set_interval(self, interval: int):
        self._interval_sec = interval

    def set_timeout(self, timeout: int):
        self._timeout_sec = timeout

    def set_retries(self, retries: int):
        self._retries = retries

    def set_start_period(self, start_period: int):
        self._start_period_sec = start_period

    def set_start_interval(self, start_interval: int):
        self._start_interval_sec = start_interval

    def has_healthcheck(self):
        return not self._use_built_in

    def render(self):
        if self._use_built_in:
            return RenderError("Should not be called when built in healthcheck is used")

        if self._disabled:
            return {"disable": True}

        if not self._test:
            raise RenderError("Healthcheck test is not set")

        return {
            "test": self._get_test(),
            "retries": self._retries,
            "interval": f"{self._interval_sec}s",
            "timeout": f"{self._timeout_sec}s",
            "start_period": f"{self._start_period_sec}s",
            "start_interval": f"{self._start_interval_sec}s",
        }


def test_mapping(variant: str, config: dict | None = None) -> list[str]:
    config = config or {}
    tests = {
        "curl": curl_test,
        "wget": wget_test,
        "http": http_test,
        "netcat": netcat_test,
        "tcp": tcp_test,
        "redis": redis_test,
        "postgres": postgres_test,
        "mariadb": mariadb_test,
        "mongodb": mongodb_test,
    }

    if variant not in tests:
        raise RenderError(f"Test variant [{variant}] is not valid. Valid options are: [{', '.join(tests.keys())}]")

    return tests[variant](config)


def get_key(config: dict, key: str, default: Any, required: bool):
    if key not in config:
        if not required:
            return default
        raise RenderError(f"Expected [{key}] to be set")
    return config[key]


def curl_test(config: dict) -> list[str]:
    config = config or {}
    port = get_key(config, "port", None, True)
    path = valid_http_path_or_raise(get_key(config, "path", "/", False))
    scheme = get_key(config, "scheme", "http", False)
    host = get_key(config, "host", "127.0.0.1", False)
    headers = get_key(config, "headers", [], False)
    method = get_key(config, "method", "GET", False)
    data = get_key(config, "data", None, False)

    cmd = ["CMD", "curl", "--request", method, "--silent", "--output", "/dev/null", "--show-error", "--fail"]

    if scheme == "https":
        cmd.append("--insecure")

    for header in headers:
        if not header[0] or not header[1]:
            raise RenderError("Expected [header] to be a list of two items for curl test")
        cmd.extend(["--header", f"{header[0]}: {header[1]}"])

    if data is not None:
        cmd.extend(["--data", json.dumps(data)])

    cmd.append(f"{scheme}://{host}:{port}{path}")
    return cmd


def wget_test(config: dict) -> list[str]:
    config = config or {}
    port = get_key(config, "port", None, True)
    path = valid_http_path_or_raise(get_key(config, "path", "/", False))
    scheme = get_key(config, "scheme", "http", False)
    host = get_key(config, "host", "127.0.0.1", False)
    headers = get_key(config, "headers", [], False)
    spider = get_key(config, "spider", True, False)

    cmd = ["CMD", "wget", "--quiet"]

    if spider:
        cmd.append("--spider")
    else:
        cmd.extend(["-O", "/dev/null"])

    if scheme == "https":
        cmd.append("--no-check-certificate")

    for header in headers:
        if not header[0] or not header[1]:
            raise RenderError("Expected [header] to be a list of two items for wget test")
        cmd.extend(["--header", f"{header[0]}: {header[1]}"])

    cmd.append(f"{scheme}://{host}:{port}{path}")

    return cmd


def http_test(config: dict) -> list[str]:
    config = config or {}
    port = get_key(config, "port", None, True)
    path = valid_http_path_or_raise(get_key(config, "path", "/", False))
    host = get_key(config, "host", "127.0.0.1", False)

    hc = f"""{{ printf "GET {path} HTTP/1.1\\r\\nHost: {host}\\r\\nConnection: close\\r\\n\\r\\n" >&0; grep "HTTP" | grep -q "200"; }} 0<>/dev/tcp/{host}/{port}"""  # noqa
    return ["CMD-SHELL", f"/bin/bash -c '{hc}'"]


def netcat_test(config: dict) -> list[str]:
    config = config or {}
    port = get_key(config, "port", None, True)
    host = get_key(config, "host", "127.0.0.1", False)
    udp_mode = get_key(config, "udp", False, False)
    cmd = ["CMD", "nc", "-z", "-w", "1"]

    if udp_mode:
        cmd.append("-u")

    cmd.extend([host, str(port)])

    return cmd


def tcp_test(config: dict) -> list[str]:
    config = config or {}
    port = get_key(config, "port", None, True)
    host = get_key(config, "host", "127.0.0.1", False)

    return ["CMD", "timeout", "1", "bash", "-c", f"cat < /dev/null > /dev/tcp/{host}/{port}"]


def redis_test(config: dict) -> list[str]:
    config = config or {}
    port = get_key(config, "port", 6379, False)
    host = get_key(config, "host", "127.0.0.1", False)
    password = get_key(config, "password", None, False)
    cmd = ["CMD", "redis-cli", "-h", host, "-p", str(port)]

    if password:
        cmd.extend(["-a", password])

    cmd.append("ping")

    return cmd


def postgres_test(config: dict) -> list[str]:
    config = config or {}
    port = get_key(config, "port", 5432, False)
    host = get_key(config, "host", "127.0.0.1", False)
    user = get_key(config, "user", None, True)
    db = get_key(config, "db", None, True)

    return ["CMD", "pg_isready", "-h", host, "-p", str(port), "-U", user, "-d", db]


def mariadb_test(config: dict) -> list[str]:
    config = config or {}
    port = get_key(config, "port", 3306, False)
    host = get_key(config, "host", "127.0.0.1", False)
    password = get_key(config, "password", None, True)

    return [
        "CMD",
        "mariadb-admin",
        "--user=root",
        f"--host={host}",
        f"--port={port}",
        f"--password={password}",
        "ping",
    ]


def mongodb_test(config: dict) -> list[str]:
    config = config or {}
    port = get_key(config, "port", 27017, False)
    host = get_key(config, "host", "127.0.0.1", False)
    db = get_key(config, "db", None, True)

    return [
        "CMD",
        "mongosh",
        "--host",
        host,
        "--port",
        str(port),
        db,
        "--eval",
        'db.adminCommand("ping")',
        "--quiet",
    ]
