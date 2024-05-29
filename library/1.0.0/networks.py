from . import utils
from typing import Dict, Any

# item_format = {
#     # The key name for the network, this get expanded with the project name
#     "name": "some-net",
#     # The name of the network (optional, if this set it will be set explicitly)
#     "net_name": "some-net",
#     # Disables or enables the network
#     "enabled": True,
#     # Defines which containers will join this network
#     "targets": [
#         {
#             "container_name": "some-container",
#             "aliases": [
#                 "some-alias",
#             ],
#             "ipv4_address": "192.168.0.1",
#             "ipv6_address": "2001:db8::1",
#             "mac_address": "00:11:22:33:44:55",
#         },
#     ],
#     # Define custom network driver
#     "driver": "some-driver",
#     # Define custom network driver options
#     "driver_opts": {
#         "op1": "val1",
#         "op2": "val2",
#     },
#     "external": False,
#     "internal": False,
#     # Define custom network ipam options
#     "ipam": {
#         "driver": "some-ipam-driver",
#         "config": [
#             {
#                 "subnet": "192.168.0.0/16",
#                 "gateway": "192.168.0.1",
#                 "ip_range": "192.168.0.2/32",
#                 "aux_addresses": {
#                     "ip1": "192.168.0.3",
#                     "ip2": "192.168.0.4",
#                 },
#             }
#         ],
#         "options": {
#             "opt1": "val1",
#             "opt2": "val2",
#         },
#     },
# }


def render_networks(values: Dict[str, Any] = {}) -> Dict[str, Any]:
    """
    Processes network configurations and returns a dictionary of networks.
    """
    if not values or not values.get("networks"):
        return {}

    networks = {}
    req_keys = ["name", "targets"]

    for item in values["networks"]:
        if not item or not item.get("enabled"):
            continue

        for key in req_keys:
            if not item.get(key):
                utils.throw_error(f"Expected [{key}] to be set for network [{item.get('name', '???')}]")

        if item["name"] in networks:
            utils.throw_error(f"Duplicate network name [{item['name']}]")

        net = networks[item["name"]] = {}

        if item.get("net_name"):
            net["name"] = item["net_name"]

        if item.get("external") and item.get("internal"):
            utils.throw_error(f"Expected [external] or [internal], but not both for network [{item['name']}]")

        if item.get("external"):
            net["external"] = item["external"]
        if item.get("internal"):
            net["internal"] = item["internal"]

        if item.get("driver"):
            net["driver"] = item["driver"]

        if item.get("driver_opts"):
            net["driver_opts"] = {}
            for key, value in item["driver_opts"].items():
                if key in net["driver_opts"]:
                    utils.throw_error(f"Duplicate driver option [{key}] for network [{item['name']}]")
                net["driver_opts"][key] = str(value)

        ipam_result = get_ipam(item.get("ipam", {}), item["name"])
        if ipam_result:
            net["ipam"] = ipam_result

    return networks


def get_ipam(ipam: Dict[str, Any], net_name: str = "") -> Dict[str, Any]:
    """
    Processes IPAM configurations and returns a dictionary of IPAM settings.
    """
    if not ipam:
        return {}

    ipam_config = {}
    if ipam.get("driver"):
        ipam_config["driver"] = ipam["driver"]

    if ipam.get("options"):
        ipam_config["options"] = {}
        for key, value in ipam["options"].items():
            if key in ipam_config["options"]:
                utils.throw_error(f"Duplicate IPAM option [{key}] for network [{net_name}]")
            ipam_config["options"][key] = str(value)

    if ipam.get("config"):
        ipam_config["config"] = []
        for config in ipam["config"]:
            cfg = get_ipam_config(config, net_name)
            if cfg:
                ipam_config["config"].append(cfg)

    return ipam_config


def get_ipam_config(config: Dict[str, Any], net_name: str = "") -> Dict[str, Any]:
    """
    Processes individual IPAM configuration entries.
    """
    ipam_config = {}

    if config.get("subnet"):
        ipam_config["subnet"] = utils.must_valid_range(config["subnet"], f"Expected [subnet] to be a valid IP network range for network [{net_name}], got [{config['subnet']}]")

    if config.get("gateway"):
        ipam_config["gateway"] = utils.must_valid_ip(config["gateway"], f"Expected [gateway] to be a valid IP address for network [{net_name}], got [{config['gateway']}]")

    if config.get("ip_range"):
        ipam_config["ip_range"] = utils.must_valid_range(config["ip_range"], f"Expected [ip_range] to be a valid IP network range for network [{net_name}], got [{config['ip_range']}]")

    if config.get("aux_addresses"):
        ipam_config["aux_addresses"] = {}
        for key, value in config["aux_addresses"].items():
            if key in ipam_config["aux_addresses"]:
                utils.throw_error(f"Duplicate aux address [{key}] for network [{net_name}]")

            ipam_config["aux_addresses"][key] = utils.must_valid_ip(value, f"Expected [aux_addresses] to be a valid IP address for network [{net_name}], got [{value}]")

    return ipam_config


def get_selected_networks_for_container(container: str, values: Dict[str, Any] = {}) -> Dict[str, Any]:
    """
    Returns a list of network configs to apply to the given container.
    """
    if not values or not values.get("networks"):
        return []

    networks = {}
    for item in values["networks"]:
        if not item or not item.get("enabled"):
            continue

        target_container = {}
        for tar in item["targets"]:
            if not tar.get("container_name"):
                utils.throw_error(f"Expected [container_name] to be set for network [{item['name']}]")
            if tar["container_name"] != container:
                continue
            target_container = tar

        if not target_container:
            continue

        networks[item["name"]] = {}
        for alias in target_container.get("aliases", []):
            if alias in networks[item["name"]]["aliases"]:
                utils.throw_error(f"Duplicate alias [{alias}] for network [{item['name']}]")
            networks[item["name"]]["aliases"].append(alias)

        if target_container.get("ipv4_address"):
            networks[item["name"]]["ipv4_address"] = utils.must_valid_ip(target_container["ipv4_address"], f"Expected [ipv4_address] to be a valid IP address for network [{item['name']}], got [{target_container['ipv4_address']}]")

        if target_container.get("ipv6_address"):
            networks[item["name"]]["ipv6_address"] = utils.must_valid_ip(target_container["ipv6_address"], f"Expected [ipv6_address] to be a valid IP address for network [{item['name']}], got [{target_container['ipv6_address']}]")

        if target_container.get("mac_address"):
            networks[item["name"]]["mac_address"] = utils.must_valid_mac(target_container["mac_address"], f"Expected [mac_address] to be a valid MAC address for network [{item['name']}], got [{target_container['mac_address']}]")

    return networks
