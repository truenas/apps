import re

from . import utils


def resources(resources, disable_resource_limits=False):
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

    if disable_resource_limits:
        del result["limits"]

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
    for pci, gpu in gpus.get("nvidia_gpu_selection", {}).items():
        if gpu["use_gpu"]:
            if not gpu.get("uuid"):
                utils.throw_error(
                    "Expected [uuid] to be set for GPU in"
                    f"slot [{pci}] in [nvidia_gpu_selection]"
                )
            device_ids.append(gpu["uuid"])

    if not device_ids:
        return {}

    return {
        "capabilities": ["gpu"],
        "driver": "nvidia",
        "device_ids": device_ids,
    }


disallowed_devices = ["/dev/dri"]


# Returns the top level devices list
# Accepting other_devices to allow manually adding devices
# directly to the list. (Eg sound devices)
def get_devices(resources: dict, other_devices: list = []) -> list:
    devices = []
    if resources.get("gpus", {}).get("use_all_gpus", False):
        devices.append("/dev/dri:/dev/dri")

    added_host_devices: list = []
    for device in other_devices:
        host_device = device.get("host_device", "").rstrip("/")
        container_device = device.get("container_device", "") or host_device
        if not host_device:
            utils.throw_error(f"Expected [host_device] to be set for device [{device}]")
        if not utils.valid_path(host_device):
            utils.throw_error(
                f"Expected [host_device] to be a valid path for device [{device}]"
            )
        if host_device in disallowed_devices:
            utils.throw_error(
                f"Device [{host_device}] is not allowed to be manually added."
            )
        if host_device in added_host_devices:
            utils.throw_error(
                f"Expected devices to be unique, but [{host_device}] was already added."
            )
        devices.append(f"{host_device}:{container_device}")
        added_host_devices.append(host_device)

    return devices
