import re

from . import utils


def resources(data):
    cpus = str(data.get("limits", {}).get("cpus", 2.0))
    memory = str(data.get("limits", {}).get("memory", 4096))
    if not re.match(r"^[1-9][0-9]*(\.[0-9]+)?$", cpus):
        utils.throw_error(f"Expected cpus to be a number or a float, got [{cpus}]")
    if not re.match(r"^[1-9][0-9]*$", memory):
        raise ValueError(f"Expected memory to be a number, got [{memory}]")

    return {
        "limits": {"cpus": cpus, "memory": f"{memory}M"},
    }
