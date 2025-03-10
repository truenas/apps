from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from render import Render


class Notes:
    def __init__(self, render_instance: "Render"):
        self._render_instance = render_instance
        self._app_name: str = ""
        self._app_train: str = ""
        self._warnings: list[str] = []
        self._deprecations: list[str] = []
        self._header: str = ""
        self._body: str = ""
        self._footer: str = ""

        self._auto_set_app_name()
        self._auto_set_app_train()
        self._auto_set_header()
        self._auto_set_footer()

    def _is_enterprise_train(self):
        if self._app_train == "enterprise":
            return True

    def _auto_set_app_name(self):
        app_name = self._render_instance.values.get("ix_context", {}).get("app_metadata", {}).get("title", "")
        self._app_name = app_name or "<app_name>"

    def _auto_set_app_train(self):
        app_train = self._render_instance.values.get("ix_context", {}).get("app_metadata", {}).get("train", "")
        self._app_train = app_train or "<app_train>"

    def _auto_set_header(self):
        self._header = f"# {self._app_name}\n\n"

    def _auto_set_footer(self):
        url = "https://github.com/truenas/apps"
        if self._is_enterprise_train():
            url = "https://ixsystems.atlassian.net"
        footer = "## Bug Reports and Feature Requests\n\n"
        footer += "If you find a bug in this app or have an idea for a new feature, please file an issue at\n"
        footer += f"{url}\n\n"
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
