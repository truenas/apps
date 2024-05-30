from . import utils
from typing import Dict, Any, List

item_format = {
    "enabled": True,
    # The container port
    "container_port": 80,
    # The published port
    "host_port": 80,
    # The protocol
    "protocol": "tcp",
    # The mode
    "mode": "ingress",
    # The host IP
    "host_ip": "192.168.0.1",
    # The app_protocol
    "app_protocol": "http",
    # The container to use for the port
    "target": "container_name",
}


def get_selected_ports_for_container(container: str, values: Dict[str, Any] = {}) -> List[Dict[str, Any]]:
    """
    Returns a list of ports to apply to the given container.
    """
    if not values or not values.get("ports"):
        return []

    ports = []
    valid_protocols = ["tcp", "udp"]
    valid_modes = ["ingress", "host"]
    req_keys = ["target", "host_port"]
    for item in values["ports"]:
        if not item or not item.get("enabled"):
            continue
        for key in req_keys:
            if not item.get(key):
                utils.throw_error(f"Expected [{key}] to be set for port [{item['name']}]")

        if not isinstance(item["target"], str):
            utils.throw_error(f"Expected [target] to be a string for port [{item['name']}], got [{type(item['target'])}]")

        if container != item["target"]:
            continue

        port = {}
        if not item.get("host_port"):
            utils.throw_error(f"Expected [host_port] to be set for port [{item['name']}]")

        port["published"] = utils.must_valid_port(item["host_port"])

        if item.get("container_port"):
            port["target"] = utils.must_valid_port(item["container_port"])
        else:  # If container port is not specified, use the same as host port
            port["target"] = port["published"]

        if item.get("protocol"):
            if item["protocol"] not in valid_protocols:
                utils.throw_error(f"Expected [protocol] to be one of {valid_protocols}, got [{item['protocol']}]")
            port["protocol"] = item["protocol"]

        if item.get("mode"):
            if item["mode"] not in valid_modes:
                utils.throw_error(f"Expected [mode] to be one of {valid_modes}, got [{item['mode']}]")
            port["mode"] = item["mode"]

        if item.get("host_ip"):
            port["host_ip"] = utils.must_valid_ip(item["host_ip"], f"Expected [host_ip] to be a valid IP address, got [{item['host_ip']}]")

        ports.append(port)

    return ports
