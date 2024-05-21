from . import utils


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
            "memory": data.get("limits", limits["memory"]).get("memory", limits["memory"]),
        }
    )

    return limits


def resources(data={}):
    return {
        "resources": {"limits": get_limits(data)},
    }
