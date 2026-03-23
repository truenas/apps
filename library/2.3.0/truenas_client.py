from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from render import Render

try:
    from .error import RenderError
    from .validations import is_truenas_system
except ImportError:
    from error import RenderError
    from validations import is_truenas_system


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


@dataclass
class PortCombo:
    bindip: str
    port: int


class TNClient:
    def __init__(self, render_instance: "Render"):
        self.client = TrueNASClient()
        self._render_instance = render_instance
        self._app_name: str = self._render_instance.values.get("ix_context", {}).get("app_name", "") or "unknown"

    def validate_ip_port_combos(self, combos: list[PortCombo]) -> None:
        try:
            return self._validation_ip_port_combos(combos)
        except RenderError:
            raise
        except Exception as e:
            if "Method does not exist" in str(e):
                # If the method does not exist, it means we are on an older version of TrueNAS
                # that does not have the combined validation endpoint
                for combo in combos:
                    self._validate_ip_port_combo(combo.bindip, combo.port)
            # In any other case, we want to silently ignore the error and not block the user from deploying their app
            pass

    def _format_err(self, lines: list[str]) -> str:
        return "The following IP:port combinations are already in use:\n" + "".join(lines)

    def _get_err_lines(self, conflicts: list[tuple[str, str, int]]) -> list[str]:
        # Example of each conflict: [schema, err_msg, errno]
        lines: list[str] = []
        for conflict in conflicts:
            # This shouldn't happen, but let's not crash if it does
            if len(conflict) != 3:
                continue

            # The port is being used by following services:
            # 1) "$bindip:$port" used by Applications ('$app_name' application)
            # 2) "$bindip:$port" used by WebUI Service
            errs = conflict[1].removeprefix("The port is being used by following services:\n").split("\n")

            # Reformat the error lines to be more readable
            # Example of each err:
            # - "$bindip:$port" used by Applications ('$app_name' application)
            # - "$bindip:$port" used by WebUI Service
            errs = [err.split(") ", 1)[-1] for err in errs if ") " in err]
            for err_line in errs:
                if f"Applications ('{self._app_name}' application)" in err_line:
                    # During upgrade, we want to ignore the error if it is related to the current app
                    continue
                lines.append(f'- "{err_line}"\n')

        return lines

    def _validation_ip_port_combos(self, combos: list[PortCombo]) -> None:
        try:
            # Convert PortCombo objects to dicts for JSON serialization
            combo_dicts = [asdict(combo) for combo in combos]
            result: list[tuple[str, str]] | None = self.client.call(
                "port.validate_ports", f"render.{self._app_name}.schema", combo_dicts, None, False
            )

            if not result:
                return

            lines = self._get_err_lines(result)
            if lines:
                # If there are conflicts, raise an error
                raise RenderError(self._format_err(lines)) from None

        except RenderError:
            raise
        except Exception as e:
            # Re-raise "Method does not exist" so the fallback can catch it
            if "Method does not exist" in str(e):
                raise
            pass

    def _validate_ip_port_combo(self, ip: str, port: int) -> None:
        schema = f"render.{self._app_name}.schema"
        try:
            self.client.call("port.validate_port", f"render.{self._app_name}.schema", port, ip, None, True)
        except ValidationErrors as e:
            err_str = str(e)
            conflict = [schema, err_str, 22]  # Errno 22 is EINVAL, which is what TrueNAS returns for port conflicts
            lines = self._get_err_lines([conflict])
            if lines:
                # If there are conflicts, raise an error
                raise RenderError(self._format_err(lines)) from None
        except Exception:
            pass
