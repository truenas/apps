from . import utils


def check_health(test, interval=10, timeout=10, retries=5, start_period=30):
    if not test:
        utils.throw_error("Expected [test] to be set")

    return {
        "test": test,
        "interval": f"{interval}s",
        "timeout": f"{timeout}s",
        "retries": retries,
        "start_period": f"{start_period}s",
    }


def pg_test(user, db, host="127.0.0.1", port=5432):
    if not user or not db:
        utils.throw_error("Postgres container: [user] and [db] must be set")
    return f"pg_isready -h {host} -p {port} -d {db} -U {user}"


def curl_test(port, path, headers=[], scheme="http", host="127.0.0.1"):
    if not port or not path or not host or not scheme:
        utils.throw_error("Expected [port], [path], [host] and [scheme] to be set")

    opts = []
    if scheme == "https":
        opts.append("--insecure")
    for header in headers:
        if not header[0] or not header[1]:
            utils.throw_error("Expected [header] to be a list of two items")
        opts.append(f'--header "{header[0]}: {header[1]}"')
    return f"curl --silent --output /dev/null --show-error --fail {' '.join(opts)} {scheme}://{host}:{port}{path}"


def wget_test(port, path, headers=[], scheme="http", host="127.0.0.1"):
    if not port or not path or not host or not scheme:
        utils.throw_error("Expected [port], [path], [host] and [scheme] to be set")

    opts = []
    if scheme == "https":
        opts.append("--no-check-certificate")
    for header in headers:
        if not header[0] or not header[1]:
            utils.throw_error("Expected [header] to be a list of two items")
        opts.append(f'--header "{header[0]}: {header[1]}"')

    return f"wget --spider --quiet {' '.join(opts)} {scheme}://{host}:{port}{path}"


def http_test(port, path, host="127.0.0.1"):
    if not port or not path:
        utils.throw_error("Expected [port] and [path] to be set")

    return f"/bin/bash -c 'exec {{health_check_fd}}<>/dev/tcp/{host}/{port} && echo -e \"GET {path} HTTP/1.1\\r\\nHost: {host}\\r\\nConnection: close\\r\\n\\r\\n\" >&$${{health_check_fd}} && cat <&$${{health_check_fd}}'"
