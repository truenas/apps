from . import utils
from . import volumes
from . import networks
from . import configs
from . import ports
from typing import Dict, Any

item_format = {
    # The key name for the config, this get expanded with the project name
    "name": "some-container",
    # Disables or enables the config
    "enabled": True,
    # The config content
    "image": "some-image",
    # The name of the container (optional, if this set it will be set explicitly)
    "container_name": "some-container",
    "environment": {
        "ENV_VAR": "some-value",
    },
    "user_environment": {
        "USER_ENV_VAR": "some-value",
    },
    "user": "1000:1000",
    "entrypoint": ["/bin/sh", "-c"],
    "command": ["echo 'Hello World'"],
    "links": ["some-container"],
    "healthcheck": {
        "test": ["CMD", "curl", "http://localhost:8080"],
        "interval": 10,
        "timeout": 3,
        "retries": 3,
        "start_period": 5,
    },
    "depends": [{"container": "some-container", "condition": "service_healthy"}],
    # TODO: add more
}


def render_containers(values: Dict[str, Any] = {}) -> Dict[str, Any]:
    if not values or not values.get("containers"):
        return {}

    containers = {}
    req_keys = ["name", "image"]
    for item in values["containers"]:
        if not item or not item.get("enabled"):
            continue
        for key in req_keys:
            if not item.get(key):
                utils.throw_error(f"Expected [{key}] to be set for container [{item.get('name', '???')}]")
        if containers.get(item["name"]):
            utils.throw_error(f"Duplicate container name [{item['name']}]")

        container = containers[item["name"]] = {}
        container["image"] = item["image"]

        if item.get("container_name"):
            container["container_name"] = item["container_name"]

        if item.get("user"):
            container["user"] = item["user"]

        envs = get_envs(item.get("environment", {}), item.get("user_environment", {}))
        if envs:
            container["environment"] = envs

        vols = volumes.get_selected_volumes_for_container(item["name"], values)
        if vols:
            container["volumes"] = vols

        nets = networks.get_selected_networks_for_container(item["name"], values)
        if nets:
            container["networks"] = nets

        conf_items = configs.get_selected_configs_for_container(item["name"], values)
        if conf_items:
            container["configs"] = conf_items

        port_items = ports.get_selected_ports_for_container(item["name"], values)
        if port_items:
            container["ports"] = port_items

        if item.get("entrypoint"):
            if not isinstance(item["entrypoint"], list):
                utils.throw_error(f"Expected [entrypoint] to be a list for container [{item['name']}], got [{type(item['entrypoint'])}]")
            container["entrypoint"] = [str(e) for e in item["entrypoint"] if e]

        if item.get("command"):
            if not isinstance(item["command"], list):
                utils.throw_error(f"Expected [command] to be a list for container [{item['name']}], got [{type(item['command'])}]")
            container["command"] = [str(e) for e in item["command"] if e]

        if item.get("links"):
            if not isinstance(item["links"], list):
                utils.throw_error(f"Expected [links] to be a list for container [{item['name']}], got [{type(item['links'])}]")
            for link in item["links"]:
                if link not in [c["name"] for c in values["containers"]]:
                    utils.throw_error(f"Expected link [{link}] to point to a valid container in [{item['name']}]")
                if link in container.get("links", []):
                    utils.throw_error(f"Duplicate link [{link}] in container [{item['name']}]")
                if "links" in container:
                    container["links"].append(link)
                else:
                    container["links"] = [link]

        if item.get("healthcheck"):
            if "test" not in item["healthcheck"]:
                utils.throw_error(f"Expected [healthcheck] to have a [test] for container [{item['name']}]")

            container["healthcheck"] = {
                "test": item["healthcheck"]["test"],
                "interval": f"{item['healthcheck'].get('interval', 10)}s",
                "timeout": f"{item['healthcheck'].get('timeout', 10)}s",
                "retries": item["healthcheck"].get("retries", 5),
                "start_period": f"{item['healthcheck'].get('start_period', 30)}s",
            }
        valid_conditions = ["service_healthy", "service_completed_successfully"]
        req_dep_keys = ["container_name", "condition"]
        for dep in item.get("depends", []):
            for key in req_dep_keys:
                if not dep.get(key):
                    utils.throw_error(f"Expected [depends.{key}] to be set for container_name [{item['name']}]")
            if dep["condition"] not in valid_conditions:
                utils.throw_error(f"Expected [condition] to be one of [{', '.join(valid_conditions)}] for container [{item['name']}], got [{dep['condition']}]")
            if dep["container_name"] not in [c["name"] for c in values["containers"]]:
                utils.throw_error(f"Expected container [{dep['container_name']}] to point to a valid container in [{item['name']}]")
            x = {dep["container_name"]: {"condition": dep["condition"]}}
            if container.get("depends_on", {}):
                container["depends_on"].update(x)
            else:
                container["depends_on"] = x

    return containers


def get_envs(dev_env: dict, user_env: dict = None) -> list:
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
