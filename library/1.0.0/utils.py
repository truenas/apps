from . import validations
import secrets
import yaml
import sys


class TemplateException(Exception):
    pass


def throw_error(message):
    # When throwing a known error, hide the traceback
    # This is because the error is also shown in the UI
    # and having a traceback makes it hard for user to read
    sys.tracebacklimit = 0
    raise TemplateException(message)


def get_yaml_opts():
    return {
        "default_flow_style": False,
        "sort_keys": False,
        "indent": 2,
    }


def to_yaml(data):
    return yaml.dump(data, **get_yaml_opts())


def secure_string(length):
    return secrets.token_urlsafe(length)


def get_host_path(data, ix_volumes):
    if not data.get("type", ""):
        throw_error("Host Path Configuration: Type must be set")

    path = ""
    if data["type"] == "host_path":
        path = process_host_path(data)
    elif data["type"] == "ix_volume":
        path = process_ix_volume(data, ix_volumes)
    else:
        throw_error(f"Type [{data['type']}] is not supported")

    return validations.validate_path(path)


def process_ix_volume(data, ix_volumes):
    path = ""
    if not data.get("ix_volume_config", {}):
        throw_error("IX Volume Configuration: [ix_volume_config] must be set")

    if not data["ix_volume_config"].get("dataset_name", ""):
        throw_error(
            "IX Volume Configuration: [ix_volume_config.dataset_name] must be set"
        )

    if not ix_volumes:
        throw_error("IX Volume Configuration: [ixVolumes] must be set")

    for item in ix_volumes:
        if not item.get("hostPath", ""):
            throw_error(
                "IX Volume Configuration: [ixVolumes] item must contain [hostPath]"
            )

        if item["hostPath"].split("/")[-1] == data["ix_volume_config"]["dataset_name"]:
            path = item["hostPath"]
            break

    if not path:
        throw_error(
            "IX Volume Configuration: [ixVolumes] does not contain dataset with name"
            + f" [{data['ix_volume_config']['dataset_name']}]"
        )

    return path


def process_host_path(data):
    if not data.get("host_path_config", {}):
        throw_error("Host Path Configuration: [host_path_config] must be set")

    if not data["host_path_config"].get("path", ""):
        throw_error("Host Path Configuration: [host_path_config.path] must be set")

    return data["host_path_config"]["path"]
