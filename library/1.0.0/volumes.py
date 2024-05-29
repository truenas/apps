from . import utils
from typing import List, Dict, Any

# item_format = {
#     # The key name for the volume, this get expanded with the project name
#     "name": "some-volume",
#     # Disables or enables the volume
#     "enabled": True,
#     # The name of the volume (optional, if this set it will be set explicitly)
#     "volume_name": "some-volume",
#     # The type of the volume
#     "type": "nfs",
#     "external": False,
#     # Defines which containers will use this volume and options specific to the container
#     "targets": [
#         {
#             "container_name": "some-container",
#             "host_path": "/some/path",
#             "mount_path": "/some/path",
#             "read_only": False,
#             "bind": {
#                 "create_host_path": True,
#                 "propagation": "rprivate",
#             },
#             "tmpfs": {
#                 "size": "1g",
#                 "mode": "0777",
#             },
#             "volume": {
#                 "nocopy": True,
#                 "subPath": "/some/path",
#             }
#         }
#     ],
#     # if type is nfs, this is required
#     "nfs": {
#         "server": "192.168.0.1",
#         "path": "/some/path",
#         "options": ["some-opt=some-value"],
#     },
#     # if type is cifs, this is required
#     "cifs": {
#         "server": "192.168.0.1",
#         "path": "/some/path",
#         "username": "some-user",
#         "password": "some-password",
#         "options": ["some-opt=some-value"],
#     },
#     # Define custom volume driver
#     "driver": "some-driver",
#     "driver_opts": {
#         "type": "nfs",
#         "device": ":/some/share",
#         "o": "addr=192.168.0.1",
#     },
# }


def render_volumes(values: Dict[str, Any] = {}) -> Dict[str, Any]:
    """
    Processes volume configurations and returns a dictionary of volumes.
    """
    if not values or not values.get("volumes"):
        return {}

    volumes = {}
    req_keys = ["name", "type", "targets"]
    valid_types = ["nfs", "cifs", "volume", "host_path", "ix_volume", "tmpfs"]

    for item in values["volumes"]:
        if not item or not item.get("enabled"):
            continue

        for key in req_keys:
            if not item.get(key):
                utils.throw_error(f"Expected [{key}] to be set for volume [{item.get('name', '???')}]")

        if item["name"] in volumes:
            utils.throw_error(f"Duplicate volume name [{item['name']}]")

        if item["type"] not in valid_types:
            utils.throw_error(f"Expected [type] to be one of [{', '.join(valid_types)}] for volume [{item['name']}], got [{item['type']}]")

        vol = volumes[item["name"]] = {}

        if item.get("volume_name"):
            vol["name"] = item["volume_name"]

        if item.get("external"):
            vol["external"] = item["external"]

        if item["type"] == "nfs":
            vol["driver_opts"] = get_nfs_config(item["nfs"], item["name"])
        elif item["type"] == "cifs":
            vol["driver_opts"] = get_cifs_config(item["cifs"], item["name"])

    return volumes


def get_cifs_config(config: Dict[str, Any], vol_name: str = "") -> Dict[str, Any]:
    """
    Processes CIFS configurations and returns a dictionary of CIFS driver options.
    """
    cifs_driver_opts = {}
    req_keys = ["server", "path", "username", "password"]
    reserved_opts = ["username", "password"]

    if not config:
        utils.throw_error(f"Expected [cifs] to be set for volume [{vol_name}] of type [cifs]")

    for key in req_keys:
        if not config.get(key):
            utils.throw_error(f"Expected [{key}] to be set for volume [{vol_name}] of type [cifs]")

    opts = [f"user={config['username']}", f"password={config['password']}"]

    if config.get("options"):
        for opt in config["options"]:
            for reserved in reserved_opts:
                if opt.startswith(reserved):
                    utils.throw_error(f"Option [{reserved}] is not allowed for volume [{vol_name}] of type [cifs]")
            # TODO: validation for duplicate options
            opts.append(opt)

    server = config["server"].lstrip("/")
    path = config["path"].lstrip("/")
    cifs_driver_opts = {
        "type": "cifs",
        "device": f"//{server}/{path}",
        "o": f"{','.join(opts)}",
    }

    return cifs_driver_opts


def get_nfs_config(config: Dict[str, Any], vol_name: str = "") -> Dict[str, Any]:
    """
    Processes NFS configurations and returns a dictionary of NFS driver options.
    """
    nfs_driver_opts = {}
    req_keys = ["server", "path"]
    reserved_opts = ["addr"]

    if not config:
        utils.throw_error(f"Expected [nfs] to be set for volume [{vol_name}] of type [nfs]")

    for key in req_keys:
        if not config.get(key):
            utils.throw_error(f"Expected [{key}] to be set for volume [{vol_name}] of type [nfs]")

    opts = [f"addr={config['server']}"]

    if config.get("options"):
        for opt in config["options"]:
            for reserved in reserved_opts:
                if opt.startswith(reserved):
                    utils.throw_error(f"Option [{reserved}] is not allowed for volume [{vol_name}] of type [nfs]")
            # TODO: validation for duplicate options
            opts.append(opt)

    # Clean up the path
    device = config.get("path").lstrip("/").lstrip(":")
    device = f":/{device}"
    nfs_driver_opts = {
        "type": "nfs",
        "device": device,
        "o": " ".join(opts),
    }

    return nfs_driver_opts


def get_actual_vol_type(vol_type: str) -> str:
    """
    Returns the actual volume type based on the given volume type.
    """
    if vol_type in ["nfs", "cifs", "volume"]:
        return "volume"
    elif vol_type in ["host_path", "ix_volume"]:
        return "bind"
    elif vol_type == "tmpfs":
        return "tmpfs"


def get_selected_volumes_for_container(container: str, values: Dict[str, Any] = {}) -> List[Dict[str, Any]]:
    """
    Returns a list of volume configs to apply to the given container.
    """
    if not values or not values.get("volumes"):
        return []

    volumes = []
    for item in values["volumes"]:
        if not item or not item.get("enabled"):
            continue

        target_container = {}
        for tar in item["targets"]:
            if not tar.get("container_name"):
                utils.throw_error(f"Expected [container_name] to be set for volume [{item['name']}]")
            if tar["container_name"] != container:
                continue
            target_container = tar

        if not target_container:
            continue

        if not target_container.get("mount_path"):
            utils.throw_error(f"Expected [mount_path] to be set for volume [{item['name']}]")

        vol = {
            "type": get_actual_vol_type(item["type"]),
            "source": item["volume_name"] if item.get("volume_name") else item["name"],
            "target": utils.must_valid_path(target_container["mount_path"]),
            "read_only": target_container.get("read_only", False),
        }
        if item["type"] in ["host_path", "ix_volume"]:
            if not target_container.get("host_path"):
                utils.throw_error(f"Expected [host_path] to be set for volume [{item['name']}]")
            # TODO: handle ix_volume's host_path
            vol["source"] = utils.must_valid_path(target_container["host_path"])
            bind_opts = target_container.get("bind", {})
            vol.update({"bind": {"create_host_path": bind_opts.get("create_host_path", True), "propagation": bind_opts.get("propagation", "rprivate")}})
        elif item["type"] == "volume":
            vol_opts = target_container.get("volume", {})
            vol_config = {}
            if "nocopy" in vol_opts:
                vol_config["nocopy"] = vol_opts["nocopy"]
            if vol_opts.get("subPath"):
                vol_config["subPath"] = vol_opts.get("subPath")
        elif item["type"] == "tmpfs":
            vol.pop("source", None)
            tmpfs_opts = target_container.get("tmpfs", {})
            tmpfs_config = {}
            if tmpfs_opts.get("size"):
                tmpfs_config["size"] = tmpfs_opts.get("size")
            if tmpfs_opts.get("mode"):
                tmpfs_config["mode"] = tmpfs_opts.get("mode")
            if tmpfs_config:
                vol.update({"tmpfs": tmpfs_config})

        volumes.append(vol)

    return volumes
