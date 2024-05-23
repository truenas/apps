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
