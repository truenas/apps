from base_v1_0_0 import utils


def validate(data):
    multi_mode = data["multi_mode"]
    storage = data["storage"]
    if len(storage["data_dirs"]) == 0:
        utils.throw_error("At least 1 storage item must be set")

    if len(storage["data_dirs"]) > 1 and not multi_mode["enabled"]:
        utils.throw_error("[Multi Mode] must be enabled if more than 1 storage item is set")

    # make sure mount_paths in data["storage"]["data_dirs"] are unique
    mount_paths = [item["mount_path"] for item in storage["data_dirs"]]
    if len(mount_paths) != len(set(mount_paths)):
        utils.throw_error(f"Mount paths in storage items must be unique, found duplicates: [{', '.join(mount_paths)}]")

    if multi_mode["enabled"]:
        if len(multi_mode["items"]) == 0:
            utils.throw_error("When [Multi Mode] is enabled, at least 1 item in must be defined.")
        disallowed_keys = ["server"]
        for item in multi_mode["items"]:
            if item in disallowed_keys:
                utils.throw_error(f"MinIO: Value [{item}] is not allowed in [Multi Mode] items")

            # /data{1...4}
            if item.startswith("/"):
                # check if these characters exist in item
                if any(char in item for char in ["{", "}"]) and "..." not in item:
                    utils.throw_error("MinIO: [Multi Mode] items must have 3 dots when they are paths with expansion eg [/some_path{1...4}]")
