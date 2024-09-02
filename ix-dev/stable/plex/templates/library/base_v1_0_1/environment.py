from . import utils
from .resources import get_nvidia_gpus_reservations


def envs(app: dict | None = None, user: list | None = None, values: dict | None = None):
    app = app or {}
    user = user or []
    values = values or {}
    result = {}

    if not values:
        utils.throw_error("Values cannot be empty in environment.py")

    if not isinstance(user, list):
        utils.throw_error(
            f"Unsupported type for user environment variables [{type(user)}]"
        )

    # Always set TZ
    result.update({"TZ": values.get("TZ", "Etc/UTC")})

    # Update envs with nvidia variables
    if values.get("resources", {}).get("gpus", {}):
        result.update(get_nvidia_env(values.get("resources", {}).get("gpus", {})))

    # Update envs with run_as variables
    if values.get("run_as"):
        result.update(get_run_as_envs(values.get("run_as", {})))

    # Make sure we don't manually set any of the above
    for item in app.items():
        if not item[0]:
            utils.throw_error("Environment variable name cannot be empty.")
        if item[0] in result:
            utils.throw_error(
                f"Environment variable [{item[0]}] is already defined automatically from the library."
            )
        result[item[0]] = item[1]

    for item in user:
        if not item.get("name"):
            utils.throw_error("Environment variable name cannot be empty.")
        if item.get("name") in result:
            utils.throw_error(
                f"Environment variable [{item['name']}] is already defined from the application developer."
            )
        result[item["name"]] = item.get("value")

    for k, v in result.items():
        val = str(v)
        # str(bool) returns "True" or "False",
        # but we want "true" or "false"
        if isinstance(v, bool):
            val = val.lower()
        result[k] = utils.escape_dollar(val)

    return result


# Sets some common variables that most applications use
def get_run_as_envs(run_as: dict) -> dict:
    result = {}
    user = run_as.get("user")
    group = run_as.get("group")
    if user:
        result.update(
            {
                "PUID": user,
                "UID": user,
                "USER_ID": user,
            }
        )
    if group:
        result.update(
            {
                "PGID": group,
                "GID": group,
                "GROUP_ID": group,
            }
        )
    return result


def get_nvidia_env(gpus: dict) -> dict:
    reservations = get_nvidia_gpus_reservations(gpus)
    if not reservations.get("device_ids"):
        return {
            "NVIDIA_VISIBLE_DEVICES": "void",
        }

    return {
        "NVIDIA_VISIBLE_DEVICES": (
            ",".join(reservations["device_ids"])
            if reservations.get("device_ids")
            else "void"
        ),
        "NVIDIA_DRIVER_CAPABILITIES": "all",
    }
