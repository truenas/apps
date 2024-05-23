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
        utils.throw_error(f"Expected storage type to be one of [host_path, ix_volume], got {data['type']}")

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


def get_volume_type(data):
    if not data.get("type"):
        utils.throw_error("Expected [type] to be set for storage")
    if data["type"] in ["host_path", "ix_volume"]:
        return "bind"
    elif data["type"] == "tmpfs":
        return "tmpfs"
    else:
        utils.throw_error(f"Expected storage type to be one of [host_path, ix_volume], got {data['type']}")


def volume(data, ix_volumes=[]):
    vol_type = get_volume_type(data)

    volume = {
        "type": vol_type,
        "target": valid_path(data.get("mount_path", "")),
        "read_only": data.get("read_only", False),
        "create_host_path": True,  # This is what docker has as default on short-syntax
    }

    if vol_type == "bind":
        volume.update({"source": host_path(data, ix_volumes)})

    return volume
