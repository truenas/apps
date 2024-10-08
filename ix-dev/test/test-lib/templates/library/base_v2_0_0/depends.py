try:
    from .error import RenderError
    from .validations import must_be_valid_depend_condition
except ImportError:
    from error import RenderError
    from validations import must_be_valid_depend_condition


class Depends:
    def __init__(self, render_instance):
        self.render_instance = render_instance
        self.dependencies: dict[str, str] = {}

    def add_dependency(self, name: str, condition: str):
        if name in self.dependencies.keys():
            raise RenderError(f"Dependency [{name}] already added")
        if name not in self.render_instance.containers.keys():
            raise RenderError(f"Dependency [{name}] not found in defined containers")
        must_be_valid_depend_condition(condition)
        self.dependencies[name] = condition

    def has_dependencies(self):
        return len(self.dependencies) > 0

    def render(self):
        return self.dependencies
