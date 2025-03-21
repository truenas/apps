from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from render import Render

try:
    from .error import RenderError
    from .portal import Portal
except ImportError:
    from error import RenderError
    from portal import Portal


class Portals:
    def __init__(self, render_instance: "Render"):
        self._render_instance = render_instance
        self._portals: set[Portal] = set()

    def add_portal(self, config: dict):
        name = config.get("name", "Web UI")

        if name in [p._name for p in self._portals]:
            raise RenderError(f"Portal [{name}] already added")

        self._portals.add(Portal(name, config))

    def render(self):
        return [p.render() for _, p in sorted([(p._name, p) for p in self._portals])]
