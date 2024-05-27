from . import utils


# Basic validation for a path (Expand later)
def valid_path(path=""):
    if not path.startswith("/"):
        utils.throw_error("Expected [path] to start with /")

    return path


# Returns the host path for a for either a host_path or ix_volume
def host_path(data, ix_volumes=[]):
    if not data.get("type"):
        utils.throw_error("Expected [type] to be set for storage")

    path = ""
    if data["type"] == "host_path":
        path = _process_host_path(data)
    elif data["type"] == "ix_volume":
        path = _process_ix_volume(data, ix_volumes)
    else:
        utils.throw_error(f"Expected storage type to be one of [host_path, ix_volume], got [{data['type']}]")

    return valid_path(path)


# Returns a volume mount object (Used in container's "volumes" level)
def vol_mount(data, ix_volumes=[]):
    vol_type = _get_vol_mount_type(data)

    volume = {
        "type": vol_type,
        "target": valid_path(data.get("mount_path", "")),
        "read_only": data.get("read_only", False),
    }

    if vol_type == "bind":  # Default create_host_path is true in short-syntax
        volume.update({"source": host_path(data, ix_volumes), "bind": {"create_host_path": True}})
        if data.get("propagation"):
            if not data["propagation"] in _get_valid_propagations():
                utils.throw_error(f"Expected [propagation] to be one of {_get_valid_propagations()}, got [{data['propagation']}]")
            volume["bind"].update({"propagation": data["propagation"]})
        else:
            # https://docs.docker.com/storage/bind-mounts/#configure-bind-propagation
            volume["bind"].update({"propagation": "rprivate"})

    elif vol_type == "volume":
        if not data.get("volume_name"):
            utils.throw_error("Expected [volume_name] to be set for [volume] type")
        volume.update({"source": data["volume_name"]})

    return volume


# Returns a volume object (Used in top "volumes" level)
def vol(data):
    if _get_vol_mount_type(data) != "volume":
        return {}

    if not data.get("volume_name"):
        utils.throw_error("Expected [volume_name] to be set for [volume] type")

    if data["type"] == "nfs":
        volume = _process_nfs(data)
    elif data["type"] == "cifs":
        volume = _process_cifs(data)
    else:
        volume = {}

    return volume


# Takes a variable number of items (either dictionaries or
# lists of dictionaries) and returns a dictionary of volumes
def volumes(*items):
    to_process = []
    for item in items:
        if not item:
            continue
        if isinstance(item, dict):
            to_process.append(item)
        elif isinstance(item, list):
            to_process.extend(item)
    return {item["volume_name"]: vol(item) for item in to_process if _get_vol_mount_type(item) == "volume"}


def _process_host_path(data):
    if not data.get("host_path_config", {}).get("path"):
        utils.throw_error("Expected [host_path_config.path] to be set for [host_path] type")

    return data["host_path_config"]["path"]


def _process_ix_volume(data, ix_volumes):
    path = ""
    if not data.get("ix_volume_config", {}).get("dataset_name"):
        utils.throw_error("Expected [ix_volume_config.dataset_name] to be set for [ix_volume] type")

    if not ix_volumes:
        utils.throw_error("Expected [ix_volumes] to be set for [ix_volume] type")

    ds = data["ix_volume_config"]["dataset_name"]
    for item in ix_volumes:
        if item.get("hostPath", "").split("/")[-1] == ds:
            path = item["hostPath"]
            break

    if not path:
        utils.throw_error(f"Expected [ix_volumes] to contain path for dataset with name [{ds}]")

    return path


def _get_vol_mount_type(data):
    if not data.get("type"):
        utils.throw_error("Expected [type] to be set for storage")

    bind_types = ["host_path", "ix_volume", "tmpfs"]
    vol_types = ["volume", "nfs"]
    all_types = bind_types + vol_types + ["tmpfs"]

    if not data["type"] in all_types:
        utils.throw_error(f"Expected storage [type] to be one of {all_types}, got [{data['type']}]")

    if data["type"] in bind_types:
        return "bind"
    elif data["type"] in vol_types:
        return "volume"
    else:
        return data["type"]


def _get_valid_propagations():
    return ["shared", "slave", "private", "rshared", "rslave", "rprivate"]


# Constructs a volume object for a cifs type
def _process_cifs(data):
    if not data.get("cifs_config"):
        utils.throw_error("Expected [cifs_config] to be set for [cifs] type")

    required_keys = ["server", "path", "username", "password"]
    for key in required_keys:
        if not data["cifs_config"].get(key):
            utils.throw_error(f"Expected [{key}] to be set for [cifs] type")

    opts = [f"user={data['cifs_config']['username']}", f"password={data['cifs_config']['password']}"]
    if data["cifs_config"].get("options"):
        if not isinstance(data["cifs_config"]["options"], list):
            utils.throw_error("Expected [cifs_config.options] to be a list for [cifs] type")

        disallowed_opts = ["user=", "password="]
        for opt in data["cifs_config"]["options"]:
            if not isinstance(opt, str):
                utils.throw_error("Expected [cifs_config.options] to be a list of strings for [cifs] type")

            for disallowed in disallowed_opts:
                if opt.startswith(disallowed):
                    utils.throw_error(f"Expected [cifs_config.options] to not start with [{disallowed}] for [cifs] type")

            opts.append(opt)

    server = data["cifs_config"]["server"].lstrip("/")
    path = data["cifs_config"]["path"]
    volume = (
        {
            "driver_opts": {
                "type": "cifs",
                "device": f"//{server}/{path}",
                "o": f"{','.join(opts)}",
            },
        },
    )

    return volume


# Constructs a volume object for a nfs type
def _process_nfs(data):
    if not data.get("nfs_config"):
        utils.throw_error("Expected [nfs_config] to be set for [nfs] type")

    required_keys = ["server", "path"]
    for key in required_keys:
        if not data["nfs_config"].get(key):
            utils.throw_error(f"Expected [{key}] to be set for [nfs] type")

    opts = [f"addr={data['nfs_config']['server']}"]
    if data["nfs_config"].get("options"):
        if not isinstance(data["nfs_config"]["options"], list):
            utils.throw_error("Expected [nfs_config.options] to be a list for [nfs] type")

        disallowed_opts = ["addr="]
        for opt in data["nfs_config"]["options"]:
            if not isinstance(opt, str):
                utils.throw_error("Expected [nfs_config.options] to be a list of strings for [nfs] type")

            for disallowed in disallowed_opts:
                if opt.startswith(disallowed):
                    utils.throw_error(f"Expected [nfs_config.options] to not start with [{disallowed}] for [nfs] type")

            opts.append(opt)

    volume = (
        {
            "driver_opts": {
                "type": "nfs",
                "device": f":{data['nfs_config']['path']}",
                "o": f"{','.join(opts)}",
            },
        },
    )

    return volume
