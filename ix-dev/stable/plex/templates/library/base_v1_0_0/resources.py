import re

from . import utils


def resources(resources):
    gpus = resources.get("gpus", {})
    cpus = str(resources.get("limits", {}).get("cpus", 2.0))
    memory = str(resources.get("limits", {}).get("memory", 4096))
    if not re.match(r"^[1-9][0-9]*(\.[0-9]+)?$", cpus):
        utils.throw_error(f"Expected cpus to be a number or a float, got [{cpus}]")
    if not re.match(r"^[1-9][0-9]*$", memory):
        raise ValueError(f"Expected memory to be a number, got [{memory}]")

    result = {
        "limits": {"cpus": cpus, "memory": f"{memory}M"},
        "reservations": {"devices": []},
    }

    if gpus:
        gpu_result = get_nvidia_gpus_reservations(gpus)
        if gpu_result:
            # Appending to devices, as we can later extend this to support other types of devices. Eg. TPUs.
            result["reservations"]["devices"].append(get_nvidia_gpus_reservations(gpus))

    # Docker does not like empty "things" all around.
    if not result["reservations"]["devices"]:
        del result["reservations"]

    return result


def get_nvidia_gpus_reservations(gpus: dict) -> dict:
    """
    Input:
    {
        "nvidia_gpu_selection": {
            "pci_slot_0": {"uuid": "uuid_0", "use_gpu": True},
            "pci_slot_1": {"uuid": "uuid_1", "use_gpu": True},
        },
    }
    """
    if not gpus:
        return {}

    device_ids = []
    for gpu in gpus.get("nvidia_gpu_selection", {}).values():
        if gpu["use_gpu"]:
            device_ids.append(gpu["uuid"])

    if not device_ids:
        return {}

    return {
        "capabilities": ["gpu"],
        "driver": "nvidia",
        "device_ids": device_ids,
    }


# Returns the top level devices list
# Accepting other_devices to allow manually adding devices
# directly to the list. (Eg sound devices)
def get_devices(resources: dict, other_devices: list = []) -> list:
    gpus = resources.get("gpus", {})
    devices = other_devices or []
    if gpus.get("use_all_gpus", False):
        devices.append("/dev/dri")

    return devices


def get_nvidia_env(resources: dict) -> dict:
    reservations = get_nvidia_gpus_reservations(resources.get("gpus", {}))
    if not reservations.get("device_ids"):
        return {
            "NVIDIA_VISIBLE_DEVICES": "void",
        }

    return {
        "NVIDIA_VISIBLE_DEVICES": ",".join(reservations["device_ids"]),
        "NVIDIA_DRIVER_CAPABILITIES": "all",
    }
