from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from render import Render


try:
    from .error import RenderError
    from .volume_types import NfsVolume, CifsVolume, DockerVolume
except ImportError:
    from error import RenderError
    from volume_types import NfsVolume, CifsVolume, DockerVolume


class Volumes:
    def __init__(self, render_instance: "Render"):
        self._render_instance = render_instance
        self._volumes: dict[str, Volume] = {}

    def add_volume(self, source: str, storage_type: str, config: dict):
        # This method can be called many times from the volume mounts
        # Only add the volume if it is not already added, but dont raise an error
        if source == "":
            raise RenderError(f"Volume source [{source}] cannot be empty")

        if source in self._volumes:
            return

        self._volumes[source] = Volume(self._render_instance, storage_type, config)

    def has_volumes(self) -> bool:
        return bool(self._volumes)

    def render(self):
        return {name: v.render() for name, v in sorted(self._volumes.items()) if v.render() is not None}


class Volume:
    def __init__(self, render_instance: "Render", storage_type: str, config: dict):
        self._render_instance = render_instance
        self.volume_spec: dict | None = {}

        match storage_type:
            case "nfs":
                self.volume_spec = NfsVolume(self._render_instance, config).get()
            case "cifs":
                self.volume_spec = CifsVolume(self._render_instance, config).get()
            case "volume" | "temporary":
                self.volume_spec = DockerVolume(self._render_instance, config).get()
            case _:
                self.volume_spec = None
                pass

    def render(self):
        return self.volume_spec
