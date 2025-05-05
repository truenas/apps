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
        self._security: dict[str, list[str]] = {}
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

    def _prepend_warning(self, warning: str):
        self._warnings.insert(0, warning)

    def add_deprecation(self, deprecation: str):
        self._deprecations.append(deprecation)

    def set_body(self, body: str):
        self._body = body

    def scan_containers(self):
        for name, c in self._render_instance._containers.items():
            if self._security.get(name) is None:
                self._security[name] = []

            if c._privileged:
                self._security[name].append("Is running with privileged mode enabled")
            if c._user.startswith("0:"):
                self._security[name].append("Is running as root user")
            if c._user.endswith(":0"):
                self._security[name].append("Is running as root group")
            if c._ipc_mode == "host":
                self._security[name].append("Is running with host IPC namespace")
            if c._cgroup == "host":
                self._security[name].append("Is running with host cgroup namespace")
            if "no-new-privileges=true" not in c._security_opt.render():
                self._security[name].append("Is running without [no-new-privileges] security option")
            if c._tty:
                self._prepend_warning(
                    f"Container [{name}] is running with a TTY, "
                    "Logs will not appear correctly in the UI due to an [upstream bug]"
                    "(https://github.com/docker/docker-py/issues/1394)"
                )

        self._security = {k: v for k, v in self._security.items() if v}

    def render(self):
        self.scan_containers()

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

        if self._security:
            result += "## Security\n\n"
            for c_name, security in self._security.items():
                result += "### " + c_name + "\n\n"
                for s in security:
                    result += f"- {s}\n"
                result += "\n"

        if self._body:
            result += self._body.strip() + "\n\n"

        result += self._footer

        return result
