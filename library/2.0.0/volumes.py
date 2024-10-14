from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from render import Render


class Volumes:
    def __init__(self, render_instance: "Render"):
        self._render_instance = render_instance
        self._volumes: dict[str, Volume] = {}

    def add_volume(self, name: str, config: dict):
        # This method can be called many times from the volume mounts
        # Only add the volume if it is not already added, but dont raise an error
        if name in self._volumes:
            return
        self._volumes[name] = Volume(self._render_instance, config)

    def has_volumes(self) -> bool:
        return bool(self._volumes)

    def render(self):
        return {name: v.render() for name, v in sorted(self._volumes.items())}


class Volume:
    def __init__(self, render_instance: "Render", config: dict):
        self._render_instance = render_instance
        self._config = config

    def render(self):
        return self._config
