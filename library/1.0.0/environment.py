from . import utils


def envs(app: dict | None = None, user: list | None = None):
    app = app or {}
    user = user or []
    track_env = {**app}
    result = {**app}

    if not user:
        user = []
    elif isinstance(user, list):
        pass
    elif isinstance(user, dict):
        user = [{"name": k, "value": v} for k, v in user.items()]
    else:
        utils.throw_error(f"Unsupported type for user environment variables [{type(user)}]")

    for k in app.keys():
        if not k:
            utils.throw_error("Environment variable name cannot be empty.")

    for item in user:
        if not item.get("name"):
            utils.throw_error("Environment variable name cannot be empty.")
        if item.get("name") in track_env:
            utils.throw_error(
                f"Environment variable [{item['name']}] is already defined from the application developer."
            )
        track_env[item["name"]] = item.get("value")
        result[item["name"]] = item.get("value")
    return result
