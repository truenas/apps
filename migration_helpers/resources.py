from memory import transform_memory, TOTAL_MEM
from cpu import transform_cpu, CPU_COUNT


def migrate_resources(resources):
    # Handle empty resources, with sane defaults
    if not resources:
        return {
            "limits": {
                "cpus": CPU_COUNT / 2,
                "memory": f"{TOTAL_MEM / 1024 / 1024}M",
            }
        }

    return {
        "limits": {
            "cpus": transform_cpu(resources.get("limits", {}).get("cpu", "")),
            "memory": transform_memory(resources.get("limits", {}).get("memory", "")),
        }
    }
