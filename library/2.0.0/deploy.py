try:
    from .resources import Resources
except ImportError:
    from resources import Resources


class Deploy:
    def __init__(self, render_instance):
        self._render_instance = render_instance
        self._resources: Resources = Resources(self._render_instance)

    def has_deploy(self):
        return self._resources.has_resources()

    def render(self):
        if self._resources.has_resources():
            return {"resources": self._resources.render()}

        return {}
