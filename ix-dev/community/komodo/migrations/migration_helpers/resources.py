from .memory import transform_memory, TOTAL_MEM
from .cpu import transform_cpu, CPU_COUNT


def migrate_resources(resources, gpus=None, system_gpus=None):
    gpus = gpus or {}
    system_gpus = system_gpus or []

    result = {
        "limits": {
            "cpus": int((CPU_COUNT or 2) / 2),
            "memory": int(TOTAL_MEM / 1024 / 1024),
        }
    }

    if resources.get("limits", {}).get("cpu", ""):
        result["limits"].update(
            {"cpus": transform_cpu(resources.get("limits", {}).get("cpu", ""))}
        )
    if resources.get("limits", {}).get("memory", ""):
        result["limits"].update(
            {"memory": transform_memory(resources.get("limits", {}).get("memory", ""))}
        )

    gpus_result = {}
    for gpu in gpus.items() if gpus else []:
        kind = gpu[0].lower()  # Kind of gpu (amd, nvidia, intel)
        count = gpu[1]  # Number of gpus user requested

        if count == 0:
            continue

        if "amd" in kind or "intel" in kind:
            gpus_result.update({"use_all_gpus": True})
        elif "nvidia" in kind:
            sys_gpus = [
                gpu_item
                for gpu_item in system_gpus
                if gpu_item.get("error") is None
                and gpu_item.get("vendor", None) is not None
                and gpu_item.get("vendor", "").upper() == "NVIDIA"
            ]
            for sys_gpu in sys_gpus:
                if count == 0:  # We passed # of gpus that user previously requested
                    break
                guid = sys_gpu.get("vendor_specific_config", {}).get("uuid", "")
                pci_slot = sys_gpu.get("pci_slot", "")
                if not guid or not pci_slot:
                    continue

                gpus_result.update(
                    {"nvidia_gpu_selection": {pci_slot: {"uuid": guid, "use_gpu": True}}}
                )
                count -= 1

    if gpus_result:
        result.update({"gpus": gpus_result})

    return result
