from typing import Any

try:
    from .error import RenderError
    from .formatter import escape_dollar
    from .validations import must_be_valid_path
except ImportError:
    from error import RenderError
    from formatter import escape_dollar
    from validations import must_be_valid_path


class Healthcheck:
    def __init__(self, render_instance):
        self._render_instance = render_instance
        self._test: str | list[str] = ""
        self._interval_sec: int = 10
        self._timeout_sec: int = 5
        self._retries: int = 30
        self._start_period_sec: int = 10
        self._disabled: bool = False

    def _get_test(self):
        if isinstance(self._test, str):
            return escape_dollar(self._test)

        return [escape_dollar(t) for t in self._test]

    def disable_healthcheck(self):
        self._disabled = True

    def set_custom_test(self, test: str | list[str]):
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

    def render(self):
        if self._disabled:
            return {"disable": True}

        if not self._test:
            raise RenderError("Healthcheck test is not set")

        return {
            "test": self._get_test(),
            "interval": f"{self._interval_sec}s",
            "timeout": f"{self._timeout_sec}s",
            "retries": self._retries,
            "start_period": f"{self._start_period_sec}s",
        }


def test_mapping(variant: str, config: dict | None = None) -> str:
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
    }

    if variant not in tests:
        raise RenderError(f"Test variant [{variant}] is not valid. Valid options are: [{', '.join(tests.keys())}]")

    return tests[variant](config)


def get_key(config: dict, key: str, default: Any, required: bool):
    if not config.get(key):
        if not required:
            return default
        raise RenderError(f"Expected [{key}] to be set")
    return config[key]


def curl_test(config: dict) -> str:
    config = config or {}
    port = get_key(config, "port", None, True)
    path = get_key(config, "path", "/", False)
    must_be_valid_path(path)
    scheme = get_key(config, "scheme", "http", False)
    host = get_key(config, "host", "127.0.0.1", False)
    headers = get_key(config, "headers", [], False)

    opts = []
    if scheme == "https":
        opts.append("--insecure")

    for header in headers:
        if not header[0] or not header[1]:
            raise RenderError("Expected [header] to be a list of two items for curl test")
        opts.append(f'--header "{header[0]}: {header[1]}"')

    cmd = "curl --silent --output /dev/null --show-error --fail"
    if opts:
        cmd += f" {' '.join(opts)}"
    cmd += f" {scheme}://{host}:{port}{path}"
    return cmd


def wget_test(config: dict) -> str:
    config = config or {}
    port = get_key(config, "port", None, True)
    path = get_key(config, "path", "/", False)
    must_be_valid_path(path)
    scheme = get_key(config, "scheme", "http", False)
    host = get_key(config, "host", "127.0.0.1", False)
    headers = get_key(config, "headers", [], False)

    opts = []
    if scheme == "https":
        opts.append("--no-check-certificate")

    for header in headers:
        if not header[0] or not header[1]:
            raise RenderError("Expected [header] to be a list of two items for wget test")
        opts.append(f'--header "{header[0]}: {header[1]}"')

    cmd = "wget --spider --quiet"
    if opts:
        cmd += f" {' '.join(opts)}"
    cmd += f" {scheme}://{host}:{port}{path}"
    return cmd


def http_test(config: dict) -> str:
    config = config or {}
    port = get_key(config, "port", None, True)
    path = get_key(config, "path", "/", False)
    must_be_valid_path(path)
    host = get_key(config, "host", "127.0.0.1", False)

    http_cmd = "/bin/bash -c '"
    http_cmd += f"exec {{health_check_fd}}<>/dev/tcp/{host}/{port} && "
    http_cmd += f'echo -e "GET {path} HTTP/1.1\\r\\n'
    http_cmd += f"Host: {host}\\r\\n"
    http_cmd += 'Connection: close\\r\\n\\r\\n"'
    http_cmd += " >&${health_check_fd} && cat <&${health_check_fd}'"

    return http_cmd


def netcat_test(config: dict) -> str:
    config = config or {}
    port = get_key(config, "port", None, True)
    host = get_key(config, "host", "127.0.0.1", False)

    return f"nc -z -w 1 {host} {port}"


def tcp_test(config: dict) -> str:
    config = config or {}
    port = get_key(config, "port", None, True)
    host = get_key(config, "host", "127.0.0.1", False)

    return f"timeout 1 bash -c 'cat < /dev/null > /dev/tcp/{host}/{port}'"


def redis_test(config: dict) -> str:
    config = config or {}
    port = get_key(config, "port", 6379, False)
    host = get_key(config, "host", "127.0.0.1", False)

    return f"redis-cli -h {host} -p {port} -a $REDIS_PASSWORD ping | grep -q PONG"


def postgres_test(config: dict) -> str:
    config = config or {}
    port = get_key(config, "port", 5432, False)
    host = get_key(config, "host", "127.0.0.1", False)

    return f"pg_isready -h {host} -p {port} -U $POSTGRES_USERNAME -d $POSTGRES_DATABASE"


def mariadb_test(config: dict) -> str:
    config = config or {}
    port = get_key(config, "port", 3306, False)
    host = get_key(config, "host", "127.0.0.1", False)

    return f"mariadb-admin --user=root --host={host} --port={port} --password=$MARIADB_ROOT_PASSWORD ping"
