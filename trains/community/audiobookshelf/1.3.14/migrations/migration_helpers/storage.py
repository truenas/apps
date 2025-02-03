def migrate_storage_item(storage_item, include_read_only=False):
    if not storage_item:
        raise ValueError("Expected [storage_item] to be set")

    result = {}
    if storage_item["type"] == "ixVolume":
        if storage_item.get("ixVolumeConfig"):
            result = migrate_ix_volume_type(storage_item)
        elif storage_item.get("datasetName"):
            result = migrate_old_ix_volume_type(storage_item)
        else:
            raise ValueError(
                "Expected [ix_volume] to have [ixVolumeConfig] or [datasetName] set"
            )
    elif storage_item["type"] == "hostPath":
        if storage_item.get("hostPathConfig"):
            result = migrate_host_path_type(storage_item)
        elif storage_item.get("hostPath"):
            result = migrate_old_host_path_type(storage_item)
        else:
            raise ValueError(
                "Expected [host_path] to have [hostPathConfig] or [hostPath] set"
            )
    elif storage_item["type"] == "emptyDir":
        result = migrate_empty_dir_type(storage_item)
    elif storage_item["type"] == "smb-pv-pvc":
        result = migrate_smb_pv_pvc_type(storage_item)

    mount_path = storage_item.get("mountPath", "")
    if mount_path:
        result.update({"mount_path": mount_path})

    if include_read_only:
        result.update({"read_only": storage_item.get("readOnly", False)})
    return result


def migrate_smb_pv_pvc_type(smb_pv_pvc):
    smb_config = smb_pv_pvc.get("smbConfig", {})
    if not smb_config:
        raise ValueError("Expected [smb_pv_pvc] to have [smbConfig] set")

    return {
        "type": "cifs",
        "cifs_config": {
            "server": smb_config["server"],
            "path": smb_config["share"],
            "domain": smb_config.get("domain", ""),
            "username": smb_config["username"],
            "password": smb_config["password"],
        },
    }


def migrate_empty_dir_type(empty_dir):
    empty_dir_config = empty_dir.get("emptyDirConfig", {})
    if not empty_dir_config:
        raise ValueError("Expected [empty_dir] to have [emptyDirConfig] set")

    if empty_dir_config.get("medium", "") == "Memory":
        # Convert Gi to Mi
        size = empty_dir_config.get("size", 0.5) * 1024
        return {
            "type": "tmpfs",
            "tmpfs_config": {"size": size},
        }

    return {"type": "temporary"}


def migrate_old_ix_volume_type(ix_volume):
    if not ix_volume.get("datasetName"):
        raise ValueError("Expected [ix_volume] to have [datasetName] set")

    return {
        "type": "ix_volume",
        "ix_volume_config": {
            "acl_enable": False,
            "dataset_name": ix_volume["datasetName"],
        },
    }


def migrate_ix_volume_type(ix_volume):
    vol_config = ix_volume.get("ixVolumeConfig", {})
    if not vol_config:
        raise ValueError("Expected [ix_volume] to have [ixVolumeConfig] set")

    result = {
        "type": "ix_volume",
        "ix_volume_config": {
            "acl_enable": vol_config.get("aclEnable", False),
            "dataset_name": vol_config.get("datasetName", ""),
        },
    }

    if vol_config.get("aclEnable", False):
        result["ix_volume_config"].update(
            {"acl_entries": migrate_acl_entries(vol_config["aclEntries"])}
        )

    return result


def migrate_old_host_path_type(host_path):
    if not host_path.get("hostPath"):
        raise ValueError("Expected [host_path] to have [hostPath] set")

    return {
        "type": "host_path",
        "host_path_config": {
            "acl_enable": False,
            "path": host_path["hostPath"],
        },
    }


def migrate_host_path_type(host_path):
    path_config = host_path.get("hostPathConfig", {})
    if not path_config:
        raise ValueError("Expected [host_path] to have [hostPathConfig] set")

    result = {
        "type": "host_path",
        "host_path_config": {
            "acl_enable": path_config.get("aclEnable", False),
        },
    }

    if path_config.get("aclEnable", False):
        result["host_path_config"].update(
            {"acl": migrate_acl_entries(path_config.get("acl", {}))}
        )
    else:
        result["host_path_config"].update({"path": path_config["hostPath"]})

    return result


def migrate_acl_entries(acl_entries: dict) -> dict:
    entries = []
    for entry in acl_entries.get("entries", []):
        entries.append(
            {
                "access": entry["access"],
                "id": entry["id"],
                "id_type": entry["id_type"],
            }
        )

    return {
        "entries": entries,
        "options": {"force": acl_entries.get("options", {}).get("force", False)},
        "path": acl_entries["path"],
    }
