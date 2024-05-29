from . import utils

# item_format = {
#     # The key name for the config, this get expanded with the project name
#     "name": "some-config",
#     # Disables or enables the config
#     "enabled": True,
#     # The config content
#     "content": "some-content",
# }


def render_configs(values={}):
    if not values or not values.get("configs"):
        return {}

    configs = {}
    req_keys = ["name", "content"]
    for item in values["configs"]:
        if not item or not item.get("enabled"):
            continue
        for key in req_keys:
            if not item.get(key):
                utils.throw_error(f"Expected [{key}] to be set for config")
        if configs.get(item["name"]):
            utils.throw_error(f"Duplicate config name [{item['name']}]")

        configs[item["name"]] = {
            "content": str(item["content"]),
        }

    return configs
