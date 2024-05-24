from . import utils


def valid_path(path):
    if not path:
        utils.throw_error("Expected [path] to be set")
    if not path.startswith("/"):
        utils.throw_error("Expected [path] to start with /")

    return path


def host_path(data, ix_volumes=[]):
    if not data.get("type"):
        utils.throw_error("Expected [type] to be set for storage")

    path = ""
    if data["type"] == "host_path":
        path = process_host_path(data)
    elif data["type"] == "ix_volume":
        path = process_ix_volume(data, ix_volumes)
    else:
        utils.throw_error(f"Expected storage type to be one of [host_path, ix_volume], got [{data['type']}]")

    return valid_path(path)


def process_host_path(data):
    if not data.get("host_path_config"):
        utils.throw_error("Expected [host_path_config] to be set for [host_path] type")

    if not data["host_path_config"].get("path"):
        utils.throw_error("Expected [host_path_config.path] to be set for [host_path] type")

    return data["host_path_config"]["path"]


def process_ix_volume(data, ix_volumes):
    path = ""
    if not data.get("ix_volume_config"):
        utils.throw_error("Expected [ix_volume_config] to be set for [ix_volume] type")

    if not data["ix_volume_config"].get("dataset_name"):
        utils.throw_error("Expected [ix_volume_config.dataset_name] to be set for [ix_volume] type")

    if not ix_volumes:
        utils.throw_error("Expected [ix_volumes] to be set for [ix_volume] type")

    ds = data["ix_volume_config"]["dataset_name"]
    for item in ix_volumes:
        if not item.get("hostPath"):
            utils.throw_error("Expected [ix_volumes] item to contain [hostPath]")

        if item["hostPath"].split("/")[-1] == ds:
            path = item["hostPath"]
            break

    if not path:
        utils.throw_error(f"Expected [ix_volumes] to contain path for dataset with name [{ds}]")

    return path


def get_vol_mount_type(data):
    if not data.get("type"):
        utils.throw_error("Expected [type] to be set for storage")

    bind_types = ["host_path", "ix_volume", "tmpfs"]
    vol_types = ["volume", "nfs"]
    all_types = bind_types + vol_types + ["tmpfs"]
    if not data["type"] in all_types:
        utils.throw_error(f"Expected storage type to be one of {all_types}, got [{data['type']}]")

    if data["type"] in bind_types:
        return "bind"
    elif data["type"] in vol_types:
        return "volume"
    else:
        return data["type"]


def get_valid_propagation():
    return ["shared", "slave", "private", "rshared", "rslave", "rprivate"]


def vol_mount(data, ix_volumes=[]):
    vol_type = get_vol_mount_type(data)

    volume = {
        "type": vol_type,
        "target": valid_path(data.get("mount_path", "")),
        "read_only": data.get("read_only", False),
    }

    if vol_type == "bind":  # Default create_host_path is true in short-syntax
        volume.update({"source": host_path(data, ix_volumes), "bind": {"create_host_path": True}})
        if not data.get("propagation"):
            # https://docs.docker.com/storage/bind-mounts/#configure-bind-propagation
            volume["bind"].update({"propagation": "rprivate"})
        else:
            if not data["propagation"] in get_valid_propagation():
                utils.throw_error(f"Expected [propagation] to be one of {get_valid_propagation()}, got [{data['propagation']}]")
            volume["bind"].update({"propagation": data["propagation"]})

    elif vol_type == "volume":
        if not data.get("volume_name"):
            utils.throw_error("Expected [volume_name] to be set for [volume] type")
        volume.update({"source": data["volume_name"]})
        pass

    return volume


def vol(data):
    if get_vol_mount_type(data) != "volume":
        return {}

    if not data.get("volume_name"):
        utils.throw_error("Expected [volume_name] to be set for [volume] type")

    if data["type"] == "nfs":
        volume = process_nfs(data)
    elif data["type"] == "cifs":
        volume = process_cifs(data)
    else:
        volume = {data["volume_name"]: {}}

    return volume


# TODO: clean this up. maybe use jsonschema?
def process_cifs(data):
    volume = {data["volume_name"]: {"driver_opts": {"type": "cifs"}}}

    if not data.get("cifs_config"):
        utils.throw_error("Expected [cifs_config] to be set for [cifs] type")

    if not data["cifs_config"].get("path"):
        utils.throw_error("Expected [cifs_config.path] to be set for [cifs] type")
    if not data["cifs_config"].get("server"):
        utils.throw_error("Expected [cifs_config.server] to be set for [cifs] type")

    # remove leading slashes from server
    srv = data["cifs_config"]["server"].lstrip("/")
    volume[data["volume_name"]]["driver_opts"].update({"device": f"//{srv}/{data['cifs_config']['path']}"})

    if not data["cifs_config"].get("username"):
        utils.throw_error("Expected [cifs_config.username] to be set for [cifs] type")
    if not data["cifs_config"].get("password"):
        utils.throw_error("Expected [cifs_config.password] to be set for [cifs] type")

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

    volume[data["volume_name"]]["driver_opts"].update({"o": f"{','.join(opts)}"})

    return volume


def process_nfs(data):
    volume = {data["volume_name"]: {"driver_opts": {"type": "nfs"}}}

    if not data.get("nfs_config"):
        utils.throw_error("Expected [nfs_config] to be set for [nfs] type")

    if not data["nfs_config"].get("path"):
        utils.throw_error("Expected [nfs_config.path] to be set for [nfs] type")
    volume[data["volume_name"]]["driver_opts"].update({"device": f":{data['nfs_config']['path']}"})

    if not data["nfs_config"].get("server"):
        utils.throw_error("Expected [nfs_config.server] to be set for [nfs] type")
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

    volume[data["volume_name"]]["driver_opts"].update({"o": f"{','.join(opts)}"})

    return volume
