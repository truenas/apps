from base_v1_1_4 import utils


def validate(data):
    multi_mode = data["minio"]["multi_mode"]
    storage = data["storage"]
    if len(storage["data_dirs"]) == 0:
        utils.throw_error("At least 1 storage item must be set")

    if (
        len(storage["data_dirs"]) > 1
        and not multi_mode.get("enabled", False)
        and not len(multi_mode.get("entries", [])) > 0
    ):
        utils.throw_error("[Multi Mode] must be enabled and entries must be set if more than 1 storage item is set")

    # make sure mount_paths in data["storage"]["data_dirs"] are unique
    mount_paths = [item["mount_path"].rstrip("/") for item in storage["data_dirs"]]
    if len(mount_paths) != len(set(mount_paths)):
        utils.throw_error(f"Mount paths in storage items must be unique, found duplicates: [{', '.join(mount_paths)}]")

    if len(multi_mode.get("entries", [])) > 0:
        disallowed_keys = ["server"]
        for item in multi_mode["entries"]:
            if item in disallowed_keys:
                utils.throw_error(f"MinIO: Value [{item}] is not allowed in [Multi Mode] items")

            # /data{1...4}
            if item.startswith("/"):
                # check if these characters exist in item
                if any(char in item for char in ["{", "}"]) and "..." not in item:
                    utils.throw_error(
                        f"MinIO: [Multi Mode] item [{item}] must have 3 dots when they are paths"
                        + " with expansion eg [/some_path{1...4}]"
                    )


def get_commands(values):
    commands = [
        "server",
        "--address",
        f":{values['network']['api_port']}",
        "--console-address",
        f":{values['network']['console_port']}",
    ]

    if values["network"]["certificate_id"]:
        commands.append("--certs-dir")
        commands.append("/.minio/certs")

    if values["minio"]["logging"]["quiet"]:
        commands.append("--quiet")

    if values["minio"]["logging"]["anonymous"]:
        commands.append("--anonymous")

    return commands
