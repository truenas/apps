from base_v1_0_0 import utils

from jsonschema import validate as json_validate, exceptions

host_storage_schema = {
    "type": "object",
    "required": ["host_path_config"],
    "properties": {
        "host_path_config": {
            "type": "object",
            "required": ["path"],
            "properties": {"path": {"type": "string"}},
        }
    },
}

ix_storage_schema = {
    "type": "object",
    "required": ["ix_volume_config"],
    "properties": {
        "ix_volume_config": {
            "type": "object",
            "required": ["dataset_name"],
            "properties": {"dataset_name": {"type": "string"}},
        }
    },
}

json_schema = {
    "type": "object",
    "properties": {
        "minio": {
            "type": "object",
            "required": ["access_key", "secret_key", "user", "group"],
            "properties": {
                "access_key": {"type": "string", "minLength": 5},
                "secret_key": {"type": "string", "minLength": 8},
                "user": {"type": "integer", "min": 568, "default": 568},
                "group": {"type": "integer", "min": 568, "default": 568},
                "logging": {
                    "type": "object",
                    "required": ["quiet", "anonymous"],
                    "properties": {
                        "quiet": {"type": "boolean", "default": False},
                        "anonymous": {"type": "boolean", "default": False},
                    },
                },
            },
        },
        "logsearch": {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean", "default": False},
                "disk_capacity_gb": {"type": "integer", "default": 10},
                "postgres_password": {"type": "string", "minLength": 8},
                "postgres_data": {
                    "type": "object",
                    "required": [
                        "type",
                    ],
                    "properties": {
                        "type": {"type": "string"},
                    },
                    "oneOf": [
                        {
                            **host_storage_schema,
                        },
                        {
                            **ix_storage_schema,
                        },
                    ],
                },
            },
            "if": {"properties": {"enabled": {"const": True}}},
            "then": {"required": ["postgres_password", "disk_capacity_gb"]},
        },
        "storage": {
            "type": "object",
            "required": ["data"],
            "properties": {
                "data": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "required": ["type", "mount_path"],
                        "properties": {
                            "type": {"type": "string"},
                            "mount_path": {"type": "string"},
                        },
                        "oneOf": [
                            {
                                **host_storage_schema,
                            },
                            {
                                **ix_storage_schema,
                            },
                        ],
                    },
                }
            },
        },
    },
}


def validate(data):
    try:
        json_validate(data, json_schema)
    except exceptions.ValidationError as e:
        utils.throw_error(f"{e.message} in {e.path}")
        return

    if len(data["storage"]["data"]) > 1 and not data["minio"].get("multi_mode", {}).get(
        "enabled", False
    ):
        utils.throw_error(
            "MinIO: [Multi Mode] must be enabled if more than 1 storage item is set"
        )

    # make sure mount_paths in data['storage']['data'] are unique
    mount_paths = [item["mount_path"] for item in data["storage"]["data"]]
    if len(mount_paths) != len(set(mount_paths)):
        utils.throw_error(
            f"MinIO: Mount paths in MinIO storage must be unique, found duplicates: [{', '.join(mount_paths)}]"
        )

    if data["minio"].get("multi_mode", {}).get("enabled", False):
        disallowed_keys = ["server"]
        for item in data["minio"]["multi_mode"].get("items", []):
            if item in disallowed_keys:
                utils.throw_error(
                    f"MinIO: Value [{item}] is not allowed in [Multi Mode] items"
                )

            if item.startswith("/"):
                # check if these characters exist in item
                if any(char in item for char in ["{", "}"]) and not "..." in item:
                    utils.throw_error(
                        "MinIO: [Multi Mode] items must have 3 dots when they are paths with expansion eg [/some_path{1...4}]"
                    )

    return ""
