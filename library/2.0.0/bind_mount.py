from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from render import Render


try:
    from .volumes import Volume
    from .validations import valid_host_path_propagation
except ImportError:
    from volumes import Volume
    from validations import valid_host_path_propagation


class BindMount:
    def __init__(self, render_instance: "Render", vol: Volume):
        self._render_instance = render_instance
        self._vol: Volume = vol

        config = vol.config
        propagation = valid_host_path_propagation(config.get("propagation", "rprivate"))
        create_host_path = config.get("create_host_path", False)

        self._bind_spec: dict = {
            "bind": {
                "create_host_path": create_host_path,
                "propagation": propagation,
            }
        }

    def render(self) -> dict:
        """Render the bind mount specification."""
        return self._bind_spec
