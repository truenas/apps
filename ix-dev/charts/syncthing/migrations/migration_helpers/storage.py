def migrate_storage_item(storage_item):
    if not storage_item:
        raise ValueError("Expected [storage_item] to be set")

    result = {}
    if storage_item["type"] == "ixVolume":
        result = migrate_ix_volume_type(storage_item)
    elif storage_item["type"] == "hostPath":
        result = migrate_host_path_type(storage_item)

    mount_path = storage_item.get("mountPath", "")
    if mount_path:
        result.update({"mount_path": mount_path})

    result.update({"read_only": storage_item.get("readOnly", False)})
    return result


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
        result["host_path_config"].update({"host_path": path_config["hostPath"]})

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
        "options": {"force": acl_entries.get("force", False)},
        "path": acl_entries["path"],
    }
