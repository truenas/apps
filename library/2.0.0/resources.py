import re

try:
    from .error import RenderError
except ImportError:
    from error import RenderError

DEFAULT_CPUS = 2.0
DEFAULT_MEMORY = 4096


class Resources:
    def __init__(self, render_instance):
        self._render_instance = render_instance
        self._limits: dict = {}
        self._reservations: dict = {}
        self._nvidia_ids: set[str] = set()
        self._auto_add_cpu_from_values()
        self._auto_add_memory_from_values()
        self._auto_add_gpus_from_values()

    def _auto_add_cpu_from_values(self):
        resources = self._render_instance.values.get("resources", {})
        cpus = str(resources.get("limits", {}).get("cpus", DEFAULT_CPUS))
        if not re.match(r"^[1-9][0-9]*(\.[0-9]+)?$", cpus):
            raise RenderError(f"Expected cpus to be a number or a float, got [{cpus}]")
        self._limits.update({"cpus": cpus})

    def _auto_add_memory_from_values(self):
        resources = self._render_instance.values.get("resources", {})
        memory = str(resources.get("limits", {}).get("memory", DEFAULT_MEMORY))
        if not re.match(r"^[1-9][0-9]*$", memory):
            raise RenderError(f"Expected memory to be a number, got [{memory}]")
        self._limits.update({"memory": f"{memory}M"})

    def _auto_add_gpus_from_values(self):
        resources = self._render_instance.values.get("resources", {})
        gpus = resources.get("gpus", {}).get("nvidia_gpu_selection", {})
        if not gpus:
            return

        for pci, gpu in gpus.items():
            if gpu.get("use_gpu", False):
                if not gpu.get("uuid"):
                    raise RenderError(f"Expected [uuid] to be set for GPU in slot [{pci}] in [nvidia_gpu_selection]")
                self._nvidia_ids.add(gpu["uuid"])

        if self._nvidia_ids:
            if not self._reservations:
                self._reservations["devices"] = []
            self._reservations["devices"].append(
                {
                    "capabilities": ["gpu"],
                    "driver": "nvidia",
                    "device_ids": sorted(self._nvidia_ids),
                }
            )

    # This is only used on ix-app that we allow
    # disabling cpus and memory. GPUs are only added
    # if the user has requested them.
    def remove_cpus_and_memory(self):
        self._limits.pop("cpus", None)
        self._limits.pop("memory", None)

    def has_resources(self):
        return len(self._limits) > 0 or len(self._reservations) > 0

    def render(self):
        result = {}
        if self._limits:
            result["limits"] = self._limits
        if self._reservations:
            result["reservations"] = self._reservations

        return result
