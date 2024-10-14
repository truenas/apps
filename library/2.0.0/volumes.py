from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from render import Render

try:
    from .error import RenderError
    from .volume import Volume
except ImportError:
    from error import RenderError
    from volume import Volume


class Volumes:
    def __init__(self, render_instance: "Render"):
        self._render_instance = render_instance
        self._volumes: dict[str, Volume] = {}

    def has_volumes(self) -> bool:
        """Check if there are any top-level volumes defined."""
        return any(v.is_top_level_volume for v in self._volumes.values())

    def get_volume(self, identifier: str):
        """Retrieve a volume by its identifier."""
        if identifier not in self.volume_identifiers():
            raise RenderError(
                f"Volume [{identifier}] not found in defined volumes. "
                f"Available volumes: [{', '.join(self.volume_identifiers())}]"
            )
        return self._volumes[identifier]

    def volume_identifiers(self) -> list[str]:
        """List all volume identifiers."""
        return list(self._volumes.keys())

    def add_volume(self, identifier: str, config: dict):
        """Add a new volume with the given identifier and configuration."""
        if not identifier:
            raise RenderError("Volume name cannot be empty")
        if identifier in self._volumes:
            raise RenderError(f"Volume [{identifier}] already added.")

        self._volumes[identifier] = Volume(self._render_instance, identifier, config)

    def check_volumes(self):
        for volume in self._volumes.values():
            if not volume.is_mounted():
                raise RenderError(f"Volume [{volume.name}] is not mounted in any container.")

    def render(self) -> dict:
        """Render all top-level volumes into a dictionary suitable for Docker Compose."""
        rendered_volumes = {}
        for volume in self._volumes.values():
            if volume.is_top_level_volume:
                rendered_volumes[volume.name] = volume.render()
        return rendered_volumes
