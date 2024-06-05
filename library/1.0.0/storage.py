from . import utils

BIND_TYPES = ["host_path", "ix_volume"]
VOL_TYPES = ["volume", "nfs", "cifs"]
ALL_TYPES = BIND_TYPES + VOL_TYPES + ["tmpfs", "anonymous"]
PROPAGATION_TYPES = ["shared", "slave", "private", "rshared", "rslave", "rprivate"]


# Basic validation for a path (Expand later)
def valid_path(path=""):
    if not path.startswith("/"):
        utils.throw_error(f"Expected path [{path}] to start with /")

    # There is no reason to allow / as a path, either on host or in a container
    if path == "/":
        utils.throw_error(f"Expected path [{path}] to not be /")

    return path


# Returns a volume mount object (Used in container's "volumes" level)
def vol_mount(data, ix_volumes=[]):
    vol_type = _get_docker_vol_type(data)

    volume = {
        "type": vol_type,
        "target": valid_path(data.get("mount_path", "")),
        "read_only": data.get("read_only", False),
    }
    if vol_type == "bind":  # Default create_host_path is true in short-syntax
        volume.update(_get_bind_vol_config(data, ix_volumes))
    elif vol_type == "volume":
        volume.update(_get_volume_vol_config(data))
    elif vol_type == "tmpfs":
        volume.update(_get_tmpfs_vol_config(data))
    elif vol_type == "anonymous":
        volume["type"] = "volume"
        volume.update(_get_anonymous_vol_config(data))

    return volume


def _get_bind_vol_config(data, ix_volumes=[]):
    path = _host_path(data, ix_volumes)
    if data.get("propagation", "rprivate") not in PROPAGATION_TYPES:
        utils.throw_error(f"Expected [propagation] to be one of [{', '.join(PROPAGATION_TYPES)}], got [{data['propagation']}]")

    # https://docs.docker.com/storage/bind-mounts/#configure-bind-propagation
    return {"source": path, "bind": {"create_host_path": True, "propagation": _get_valid_propagation(data)}}


def _get_volume_vol_config(data):
    if not data.get("volume_name"):
        utils.throw_error("Expected [volume_name] to be set for [volume] type")

    return {"source": data["volume_name"], "volume": _process_volume_config(data)}


def _get_anonymous_vol_config(data):
    return {"volume": _process_volume_config(data)}


def _get_tmpfs_vol_config(data):
    tmpfs = {}
    if data.get("size"):
        if not isinstance(data["size"], int):
            utils.throw_error("Expected [size] to be an integer for [tmpfs] type")
        if not data["size"] > 0:
            utils.throw_error("Expected [size] to be greater than 0 for [tmpfs] type")
        tmpfs.update({"size": data["size"]})
    if data.get("mode"):
        if not isinstance(data["mode"], str):
            utils.throw_error("Expected [mode] to be a string for [tmpfs] type")
        tmpfs.update({"mode": data["mode"]})
    return {"tmpfs": tmpfs}


# Returns a volume object (Used in top "volumes" level)
def vol(data):
    if not data or _get_docker_vol_type(data) != "volume":
        return {}

    if not data.get("volume_name"):
        utils.throw_error("Expected [volume_name] to be set for [volume] type")

    if data["type"] == "nfs":
        return {data["volume_name"]: _process_nfs(data)}
    elif data["type"] == "cifs":
        return {data["volume_name"]: _process_cifs(data)}
    else:
        return {data["volume_name"]: {}}


def _is_host_path(data):
    return data.get("type") == "host_path"


def _get_valid_propagation(data):
    if not data.get("propagation"):
        return "rprivate"
    if not data["propagation"] in PROPAGATION_TYPES:
        utils.throw_error(f"Expected [propagation] to be one of [{', '.join(PROPAGATION_TYPES)}], got [{data['propagation']}]")
    return data["propagation"]


def _is_ix_volume(data):
    return data.get("type") == "ix_volume"


# Returns the host path for a for either a host_path or ix_volume
def _host_path(data, ix_volumes=[]):
    path = ""
    if _is_host_path(data):
        path = _process_host_path_config(data)
    elif _is_ix_volume(data):
        path = _process_ix_volume_config(data, ix_volumes)
    else:
        utils.throw_error(f"Expected [_host_path] to be called only for types [host_path, ix_volume], got [{data['type']}]")

    return valid_path(path)


# Returns the type of storage as used in docker-compose
def _get_docker_vol_type(data):
    if not data.get("type"):
        utils.throw_error("Expected [type] to be set for storage")

    if data["type"] not in ALL_TYPES:
        utils.throw_error(f"Expected storage [type] to be one of {ALL_TYPES}, got [{data['type']}]")

    if data["type"] in BIND_TYPES:
        return "bind"
    elif data["type"] in VOL_TYPES:
        return "volume"
    else:
        return data["type"]


def _process_host_path_config(data):
    if not data.get("host_path_config", {}).get("path"):
        utils.throw_error("Expected [host_path_config.path] to be set for [host_path] type")

    return data["host_path_config"]["path"]


def _process_volume_config(data):
    return {"nocopy": data.get("volume_config", {}).get("nocopy", False)}


def _process_ix_volume_config(data, ix_volumes):
    path = ""
    if not data.get("ix_volume_config", {}).get("dataset_name"):
        utils.throw_error("Expected [ix_volume_config.dataset_name] to be set for [ix_volume] type")

    if not ix_volumes:
        utils.throw_error("Expected [ix_volumes] to be set for [ix_volume] type")

    ds = data["ix_volume_config"]["dataset_name"]
    for item in ix_volumes:
        # TODO: verify the "hostPath" key is the correct from middleware side
        # Ideally we would want to have the "dataset_name" in the dict, instead of doing this check below
        if item.get("hostPath", "").split("/")[-1] == ds:
            path = item["hostPath"]
            break

    if not path:
        utils.throw_error(f"Expected [ix_volumes] to contain path for dataset with name [{ds}]")

    return path


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
    volume = {
        "driver_opts": {
            "type": "cifs",
            "device": f"//{server}/{path}",
            "o": f"{','.join(opts)}",
        },
    }

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

    volume = {
        "driver_opts": {
            "type": "nfs",
            "device": f":{data['nfs_config']['path']}",
            "o": f"{','.join(opts)}",
        },
    }

    return volume
