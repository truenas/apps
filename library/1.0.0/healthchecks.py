def check_health(test, interval=10, timeout=10, retries=5, start_period=30):
    # if kwargs is empty, use default health timings

    if not test:
        raise Exception("Healthcheck: [test] must be set")

    return {
        "test": test,
        "interval": f"{interval}s",
        "timeout": f"{timeout}s",
        "retries": retries,
        "start_period": f"{start_period}s",
    }


def pg_test(user, db, host="127.0.0.1", port=5432):
    if not user or not db:
        raise Exception("Postgres container: [user] and [db] must be set")
    return f"pg_isready -h {host} -p {port} -d {db} -U {user}"


def curl_test(url):
    if not url:
        raise Exception("Curl test: [url] must be set")
    return f"curl --silent --fail {url}"
