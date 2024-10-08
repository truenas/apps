import re

try:
    from .error import RenderError
except ImportError:
    from error import RenderError

DEFAULT_CPUS = 2.0
DEFAULT_MEMORY = 4096


class Resources:
    def __init__(self, render_instance):
        self.render_instance = render_instance
        self.limits: dict = {}
        self.reservations: dict = {}
        self.nvidia_ids: set[str] = set()
        self.auto_add_cpu_from_values()
        self.auto_add_memory_from_values()
        self.auto_add_gpus_from_values()

    def auto_add_cpu_from_values(self):
        resources = self.render_instance.values.get("resources", {})
        cpus = str(resources.get("limits", {}).get("cpus", DEFAULT_CPUS))
        if not re.match(r"^[1-9][0-9]*(\.[0-9]+)?$", cpus):
            raise RenderError(f"Expected cpus to be a number or a float, got [{cpus}]")
        self.limits.update({"cpus": cpus})

    def auto_add_memory_from_values(self):
        resources = self.render_instance.values.get("resources", {})
        memory = str(resources.get("limits", {}).get("memory", DEFAULT_MEMORY))
        if not re.match(r"^[1-9][0-9]*$", memory):
            raise RenderError(f"Expected memory to be a number, got [{memory}]")
        self.limits.update({"memory": f"{memory}M"})

    def auto_add_gpus_from_values(self):
        resources = self.render_instance.values.get("resources", {})
        gpus = resources.get("gpus", {}).get("nvidia_gpu_selection", {})
        if not gpus:
            return

        for pci, gpu in gpus.items():
            if gpu.get("use_gpu", False):
                if not gpu.get("uuid"):
                    raise RenderError("Expected [uuid] to be set for GPU in slot [{pci}] in [nvidia_gpu_selection]")
                self.nvidia_ids.add(gpu["uuid"])

        if self.nvidia_ids:
            if not self.reservations:
                self.reservations["devices"] = []
            self.reservations["devices"].append(
                {
                    "capabilities": ["gpu"],
                    "driver": "nvidia",
                    "device_ids": sorted(self.nvidia_ids),
                }
            )

    def has_resources(self):
        return len(self.limits) > 0 or len(self.reservations) > 0

    def render(self):
        result = {}
        if self.limits:
            result["limits"] = self.limits
        if self.reservations:
            result["reservations"] = self.reservations

        return result
