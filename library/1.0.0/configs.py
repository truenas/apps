from . import utils
from typing import List, Dict, Any


# item_format = {
#     # The key name for the config, this get expanded with the project name
#     "name": "some-config",
#     # Disables or enables the config
#     "enabled": True,
#     # The config content
#     "content": "some-content",
#     "targets": [
#         {
#             "container_name": "some-container",
#             "mount_path": "/some/path",
#             "uid": 123,
#             "gid": 456,
#             "mode": "0644",
#         },
#     ],
# }


def render_configs(values: Dict[str, Any] = {}) -> Dict[str, Any]:
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


def get_selected_configs_for_container(container: str, values: Dict[str, Any] = {}) -> List[Dict[str, Any]]:
    """
    Returns a list of configs to apply to the given container.
    """
    if not values or not values.get("configs"):
        return {}

    configs = []
    for item in values["configs"]:
        if not item or not item.get("enabled"):
            continue

        target_container = {}
        for tar in item["targets"]:
            if not tar.get("container_name"):
                utils.throw_error(f"Expected [container_name] to be set for config [{item['name']}]")
            if tar["container_name"] != container:
                continue
            target_container = tar

        if not target_container:
            continue

        if not target_container.get("mount_path"):
            utils.throw_error(f"Expected [mount_path] to be set for config [{item['name']}]")

        config = {"target": target_container["mount_path"]}

        if item.get("uid"):
            config.update({"uid": item["uid"]})
        if item.get("gid"):
            config.update({"gid": item["gid"]})
        if item.get("mode"):
            config.update({"mode": item["mode"]})

        configs.append(config)

    return configs
