from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from render import Render


class Notes:
    def __init__(self, render_instance: "Render"):
        self._render_instance = render_instance
        self._app_name: str = ""
        self._warnings: list[str] = []
        self._deprecations: list[str] = []
        self._header: str = ""
        self._body: str = ""
        self._footer: str = ""

        self._auto_set_app_name()
        self._auto_set_header()
        self._auto_set_footer()

    def _auto_set_app_name(self):
        app_name = self._render_instance.values.get("ix_context", {}).get("app_metadata", {}).get("name", "")
        self._app_name = app_name or "<app_name>"

    def _auto_set_header(self):
        head = "# Welcome to TrueNAS SCALE\n\n"
        head += f"Thank you for installing {self._app_name}!\n\n"
        self._header = head

    def _auto_set_footer(self):
        footer = "## Documentation\n\n"
        footer += f"Documentation for {self._app_name} can be found at https://www.truenas.com/docs.\n\n"
        footer += "## Bug reports\n\n"
        footer += "If you find a bug in this app, please file an issue at\n"
        footer += "https://ixsystems.atlassian.net or https://github.com/truenas/apps\n\n"
        footer += "## Feature requests or improvements\n\n"
        footer += "If you find a feature request for this app, please file an issue at\n"
        footer += "https://ixsystems.atlassian.net or https://github.com/truenas/apps\n"
        self._footer = footer

    def add_warning(self, warning: str):
        self._warnings.append(warning)

    def add_deprecation(self, deprecation: str):
        self._deprecations.append(deprecation)

    def set_body(self, body: str):
        self._body = body

    def render(self):
        result = self._header

        if self._warnings:
            result += "## Warnings\n\n"
            for warning in self._warnings:
                result += f"- {warning}\n"
            result += "\n"

        if self._deprecations:
            result += "## Deprecations\n\n"
            for deprecation in self._deprecations:
                result += f"- {deprecation}\n"
            result += "\n"

        if self._body:
            result += self._body.strip() + "\n\n"

        result += self._footer

        return result
