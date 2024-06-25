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


def curl_test(url):
    if not url:
        utils.throw_error("Curl test: [url] must be set")
    return f"curl --silent --output /dev/null --show-error --fail {url}"


def wget_test(url):
    if not url:
        utils.throw_error("Wget test: [url] must be set")
    return f"wget --spider --quiet {url}"


def http_test(port, path, host="127.0.0.1"):
    if not port or not path:
        utils.throw_error("Expected [port] and [path] to be set")

    return f"/bin/bash -c 'exec {{health_check_fd}}<>/dev/tcp/{host}/{port} && echo -e \"GET {path} HTTP/1.1\\r\\nHost: {host}\\r\\nConnection: close\\r\\n\\r\\n\" >&$${{health_check_fd}} && cat <&$${{health_check_fd}}'"
