from .memory import transform_memory, TOTAL_MEM
from .cpu import transform_cpu, CPU_COUNT


def migrate_resources(resources, gpus=None):
    gpus = gpus or {}

    result = {
        "limits": {
            "cpus": (CPU_COUNT or 2) / 2,
            "memory": {TOTAL_MEM / 1024 / 1024},
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

    for gpu in gpus.items() if gpus else []:
        if gpu[1] > 0 and ("amd" in gpu[0] or "intel" in gpu[0]):
            result.update({"gpus": {"use_all_gpus": True}})
            break
        # We cannot migrate NVIDIA GPUs, as we don't know the UUIDs at this point
        # and schema validation will fail.

    return result
