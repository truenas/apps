from . import utils


def check_health(test, interval=10, timeout=5, retries=30, start_period=10):
    if not test:
        utils.throw_error("Expected [test] to be set")

    return {
        "test": test,
        "interval": f"{interval}s",
        "timeout": f"{timeout}s",
        "retries": retries,
        "start_period": f"{start_period}s",
    }


def mariadb_test(db, config=None):
    config = config or {}
    if not db:
        utils.throw_error("MariaDB container: [db] must be set")

    host = config.get("host", "127.0.0.1")
    port = config.get("port", 3306)

    return f"mariadb-admin --user=root --host={host} --port={port} --password=$$MARIADB_ROOT_PASSWORD ping"


def pg_test(user, db, config=None):
    config = config or {}
    if not user or not db:
        utils.throw_error("Postgres container: [user] and [db] must be set")

    host = config.get("host", "127.0.0.1")
    port = config.get("port", 5432)

    return f"pg_isready -h {host} -p {port} -d {db} -U {user}"


def redis_test(config=None):
    config = config or {}

    host = config.get("host", "127.0.0.1")
    port = config.get("port", 6379)
    password = "$$REDIS_PASSWORD"

    return f"redis-cli -h {host} -p {port} -a {password} ping | grep -q PONG"


def curl_test(port, path, config=None):
    config = config or {}
    if not port or not path:
        utils.throw_error("Expected [port] and [path] to be set")

    scheme = config.get("scheme", "http")
    host = config.get("host", "127.0.0.1")
    headers = config.get("headers", [])

    opts = []
    if scheme == "https":
        opts.append("--insecure")

    for header in headers:
        if not header[0] or not header[1]:
            utils.throw_error("Expected [header] to be a list of two items")
        opts.append(f'--header "{header[0]}: {header[1]}"')

    return f"curl --silent --output /dev/null --show-error --fail {' '.join(opts)} {scheme}://{host}:{port}{path}"


def wget_test(port, path, config=None):
    config = config or {}
    if not port or not path:
        utils.throw_error("Expected [port] and [path] to be set")

    scheme = config.get("scheme", "http")
    host = config.get("host", "127.0.0.1")
    headers = config.get("headers", [])

    opts = []
    if scheme == "https":
        opts.append("--no-check-certificate")

    for header in headers:
        if not header[0] or not header[1]:
            utils.throw_error("Expected [header] to be a list of two items")
        opts.append(f'--header "{header[0]}: {header[1]}"')

    return f"wget --spider --quiet {' '.join(opts)} {scheme}://{host}:{port}{path}"


def http_test(port, path, config=None):
    config = config or {}
    if not port or not path:
        utils.throw_error("Expected [port] and [path] to be set")

    host = config.get("host", "127.0.0.1")

    return f"""
    /bin/bash -c 'exec {{hc_fd}}<>/dev/tcp/{host}/{port} && echo -e "GET {path} HTTP/1.1\\r\\nHost: {host}\\r\\nConnection: close\\r\\n\\r\\n" >&$${{hc_fd}} && cat <&$${{hc_fd}} | grep "HTTP/1.1 200"'
    """  # noqa


def netcat_test(port, config=None):
    config = config or {}
    if not port:
        utils.throw_error("Expected [port] to be set")

    host = config.get("host", "127.0.0.1")

    return f"nc -z -w 1 {host} {port}"


def tcp_test(port, config=None):
    config = config or {}
    if not port:
        utils.throw_error("Expected [port] to be set")

    host = config.get("host", "127.0.0.1")

    return f"timeout 1 bash -c 'cat < /dev/null > /dev/tcp/{host}/{port}'"
