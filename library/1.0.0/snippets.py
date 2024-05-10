from . import utils


def health_check(test="", interval=10, timeout=10, retries=5, start_period=30):
    if not test:
        utils.throw_error("Healtcheck: [test] must be set")

    return {
        "test": test,
        "interval": f"{interval}s",
        "timeout": f"{timeout}s",
        "retries": retries,
        "start_period": f"{start_period}s",
    }


def curl_test(url):
    return f"curl --silent --fail {url}"


def pg_test(user, db, host="127.0.0.1", port=5432):
    if not user:
        utils.throw_error("Postgres container: [user] must be set")

    if not db:
        utils.throw_error("Postgres container: [db] must be set")

    return f"pg_isready -h {host} -p {port} -d {db} -U {user}"


def postgres_uid():
    return 999


def postgres_gid():
    return 999


def postgres_run_as():
    return f"{postgres_uid()}:{postgres_gid()}"


def postgres_environment(user, password, db):
    if not user:
        utils.throw_error("Postgres container: [user] must be set")

    if not password:
        utils.throw_error("Postgres container: [password] must be set")

    if not db:
        utils.throw_error("Postgres container: [db] must be set")

    return {"POSTGRES_USER": user, "POSTGRES_PASSWORD": password, "POSTGRES_DB": db}


def get_default_limits():
    return {"cpus": "2.0", "memory": "4gb"}


def get_limits(data):
    limits = get_default_limits()

    if not data:
        return limits

    limits.update(
        {
            "cpus": str(data.get("limits", limits["cpus"]).get("cpus", limits["cpus"])),
            "memory": data.get("limits", limits["memory"]).get(
                "memory", limits["memory"]
            ),
        }
    )

    return limits


def resources(data={}):
    return {
        "resources": {"limits": get_limits(data)},
    }
