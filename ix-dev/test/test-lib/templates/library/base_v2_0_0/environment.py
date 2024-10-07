from typing import Any

try:
    from .error import RenderError
    from .resources import Resources
    from .formatter import escape_dollar
except ImportError:
    from error import RenderError
    from resources import Resources
    from formatter import escape_dollar


class Environment:
    def __init__(self, render_instance, resources: Resources):
        self.render_instance = render_instance
        self.resources = resources
        self.user_vars: dict = {}
        self.auto_variables: dict = {}
        self.app_dev_variables: dict = {}

        self.auto_add_variables_from_values()

    def auto_add_variables_from_values(self):
        self.add_generic_variables()
        self.add_nvidia_variables()

    def add_generic_variables(self):
        self.auto_variables["TZ"] = self.render_instance.values.get("TZ", "Etc/UTC")
        run_as = self.render_instance.values.get("run_as", {})
        user = run_as.get("user")
        group = run_as.get("group")
        if user:
            self.auto_variables["PUID"] = user
            self.auto_variables["UID"] = user
            self.auto_variables["USER_ID"] = user
        if group:
            self.auto_variables["PGID"] = group
            self.auto_variables["GID"] = group
            self.auto_variables["GROUP_ID"] = group

    def add_nvidia_variables(self):
        if self.resources.nvidia_ids:
            self.auto_variables["NVIDIA_DRIVER_CAPABILITIES"] = "all"
            self.auto_variables["NVIDIA_VISIBLE_DEVICES"] = ",".join(
                sorted(self.resources.nvidia_ids)
            )
        else:
            self.auto_variables["NVIDIA_VISIBLE_DEVICES"] = "void"

    def add_env(self, name: str, value: Any):
        if not name:
            raise RenderError(f"Environment variable name cannot be empty. [{name}]")
        if name in self.app_dev_variables.keys():
            raise RenderError(
                f"Found duplicate environment variable [{name}] in application developer environment variables."
            )
        self.app_dev_variables[name] = value

    def add_user_envs(self, user_env: list[dict]):
        for item in user_env:
            if not item.get("name"):
                raise RenderError(f"Environment variable name cannot be empty. [{item}]")
            if item["name"] in self.user_vars.keys():
                raise RenderError(
                    f"Found duplicate environment variable [{item['name']}] in user environment variables."
                )
            self.user_vars[item["name"]] = item.get("value")

    def format_value(self, v: Any) -> str:
        value = str(v)

        # str(bool) returns "True" or "False",
        # but we want "true" or "false"
        if isinstance(v, bool):
            value = value.lower()
        return value

    def has_variables(self):
        return (
            len(self.auto_variables) > 0
            or len(self.user_vars) > 0
            or len(self.app_dev_variables) > 0
        )

    def render(self):
        result: dict[str, str] = {}

        # Add envs from auto variables
        for k, v in self.auto_variables.items():
            result[k] = self.format_value(v)

        # Add envs from application developer (prohibit overwriting auto variables)
        for k, v in self.app_dev_variables.items():
            if k in self.auto_variables.keys():
                raise RenderError(
                    f"Environment variable [{k}] is already defined automatically from the library."
                )
            result[k] = self.format_value(v)

        # Add envs from user (prohibit overwriting app developer envs and auto variables)
        for k, v in self.user_vars.items():
            if k in self.app_dev_variables.keys() or k in self.auto_variables.keys():
                raise RenderError(
                    f"Environment variable [{k}] is already defined automatically from the application developer."
                )
            result[k] = self.format_value(v)

        return {k: escape_dollar(v) for k, v in result.items()}
