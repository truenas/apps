import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from render import Render

try:
    from .error import RenderError
except ImportError:
    from error import RenderError


def is_truenas_system():
    """Check if we're running on a TrueNAS system"""
    return "truenas" in os.uname().release


# Import based on system detection
if is_truenas_system():
    from truenas_api_client import Client as TrueNASClient

    try:
        # 25.04 and later
        from truenas_api_client.exc import ValidationErrors
    except ImportError:
        # 24.10 and earlier
        from truenas_api_client import ValidationErrors
else:
    # Mock classes for non-TrueNAS systems
    class TrueNASClient:
        def call(self, *args, **kwargs):
            return None

    class ValidationErrors(Exception):
        def __init__(self, errors):
            self.errors = errors


class Client:
    def __init__(self, render_instance: "Render"):
        self.client = TrueNASClient()
        self._render_instance = render_instance
        self._app_name: str = self._render_instance.values.get("ix_context", {}).get("app_name", "") or "unknown"
        self._is_install: bool = self._render_instance.values.get("ix_context", {}).get("is_install", False)

    def validate_ip_port_combo(self, ip: str, port: int) -> None:
        try:
            # During installation check all namespaces, including "app"
            # During upgrades, don't check "app" namespace, as it will error out as the current app uses the port.
            # Caveat is that if another app uses the same port, it will not be validated. Docker will error out.
            whitelist = None if self._is_install else "app"
            self.client.call("port.validate_port", f"render.{self._app_name}.schema", port, ip, whitelist, True)
        except ValidationErrors as e:
            raise RenderError(str(e)) from None
        except Exception:
            pass
