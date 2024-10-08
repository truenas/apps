try:
    from .error import RenderError
    from .validations import must_be_valid_depend_condition
except ImportError:
    from error import RenderError
    from validations import must_be_valid_depend_condition


class Depends:
    def __init__(self, render_instance):
        self._render_instance = render_instance
        self._dependencies: dict[str, str] = {}

    def add_dependency(self, name: str, condition: str):
        if name in self._dependencies.keys():
            raise RenderError(f"Dependency [{name}] already added")
        if name not in self._render_instance.container_names():
            raise RenderError(f"Dependency [{name}] not found in defined containers")
        must_be_valid_depend_condition(condition)
        self._dependencies[name] = condition

    def has_dependencies(self):
        return len(self._dependencies) > 0

    def render(self):
        return {d: {"condition": c} for d, c in self._dependencies.items()}
