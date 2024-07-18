import math
import psutil
import re
import os

CPU_COUNT = os.cpu_count()

NUMBER_REGEX = re.compile(r"^[1-9][0-9]$")
FLOAT_REGEX = re.compile(r"^[0-9]+\.[0-9]+$")
MILI_CPU_REGEX = re.compile(r"^[0-9]+m$")


def transform_cpu(cpu) -> int:
    result = 2
    if NUMBER_REGEX.match(cpu):
        result = int(cpu)
    elif FLOAT_REGEX.match(cpu):
        result = int(math.ceil(float(cpu)))
    elif MILI_CPU_REGEX.match(cpu):
        num = int(cpu[:-1])
        num = num / 1000
        result = int(math.ceil(num))

    if CPU_COUNT is not None:
        # Do not exceed the actual CPU count
        result = min(result, CPU_COUNT)

    return result


TOTAL_MEM = psutil.virtual_memory().total

SINGLE_SUFFIX_REGEX = re.compile(r"^[1-9][0-9]*([EPTGMK])$")
DOUBLE_SUFFIX_REGEX = re.compile(r"^[1-9][0-9]*([EPTGMK])i$")
BYTES_INTEGER_REGEX = re.compile(r"^[1-9][0-9]*$")
EXPONENT_REGEX = re.compile(r"^[1-9][0-9]*e[0-9]+$")

SUFFIX_MULTIPLIERS = {
    "K": 10**3,
    "M": 10**6,
    "G": 10**9,
    "T": 10**12,
    "P": 10**15,
    "E": 10**18,
}

DOUBLE_SUFFIX_MULTIPLIERS = {
    "Ki": 2**10,
    "Mi": 2**20,
    "Gi": 2**30,
    "Ti": 2**40,
    "Pi": 2**50,
    "Ei": 2**60,
}


def transform_memory(memory):
    result = "2g"  # Default to 2GB

    if re.match(SINGLE_SUFFIX_REGEX, memory):
        suffix = memory[-1]
        result = int(memory[:-1]) * SUFFIX_MULTIPLIERS[suffix]
    elif re.match(DOUBLE_SUFFIX_REGEX, memory):
        suffix = memory[-2:]
        result = int(memory[:-2]) * DOUBLE_SUFFIX_MULTIPLIERS[suffix]
    elif re.match(BYTES_INTEGER_REGEX, memory):
        result = int(memory)
    elif re.match(EXPONENT_REGEX, memory):
        result = int(float(memory))

    result = math.ceil(result)
    result = min(result, TOTAL_MEM)
    result = result / 1024 / 1024 / 1024
    return f"{int(result)}g"


def migrate_resources(resources):
    new_resources = {
        "limits": {
            "cpus": transform_cpu(resources.get("limits", {}).get("cpu", "")),
            "memory": transform_memory(resources.get("limits", {}).get("memory", "")),
        }
    }

    return new_resources


def migrate_dns_config(dns_config):
    if not dns_config:
        return []

    dns_opts = []
    for opt in dns_config.get("options", []):
        dns_opts.append(f"{opt['name']}:{opt['value']}")

    return dns_opts


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
