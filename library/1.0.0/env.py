from . import utils


def envs(dev_env: dict, user_env: dict = None) -> list:
    tracked_env = {}
    envs = {}
    for key, value in dev_env.items():
        envs.update({key: value})
        tracked_env[key] = True

    for key, value in user_env.items() if user_env else {}:
        if key in tracked_env:
            err = f"Key [{key}] is already defined by the application developer."
            err += " Please remove it from the user defined environment variables."
            raise utils.throw_error(err)

        envs.update({key: value})

    return envs
