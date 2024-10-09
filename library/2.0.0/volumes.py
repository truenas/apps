try:
    from .error import RenderError
except ImportError:
    from error import RenderError


class Volumes:
    def __init__(self, render_instance):
        self._render_instance = render_instance
        self._volumes: dict[str, Volume] = {}

    def has_volumes(self):
        for v in self._volumes.values():
            if v.is_top_level_volume():
                return True
        return

    def add_volume(self, name: str, config: dict):
        if name == "":
            raise RenderError("Volume name cannot be empty")
        if name in self._volumes.keys():
            raise RenderError(f"Volume [{name}] already added")
        self._volumes[name] = Volume(self._render_instance, name, config)

    def render(self):
        result: dict = {}
        for v in self._volumes.values():
            if v.is_top_level_volume():
                result[v.get_name()] = v.render()
        pass


class Volume:
    def __init__(self, render_instance, name: str, config: dict):
        self._render_instance = render_instance
        self._generated_name: str = ""
        self._volume_data: dict = {}
        self._is_top_level: bool = False

        self._create_volume(name, config)

    def _create_volume(self, name: str, config: dict):
        # Parse config
        # make sure its valid
        # generate a name
        # update self._volume_data
        # set the _is_volume when applicable
        pass

    # Not all volumes need to be defined
    # in the top level volumes section
    def is_top_level_volume(self):
        return self._is_top_level

    def get_name(self):
        return self._generated_name

    def render(self):
        if self.is_top_level_volume():
            return self._volume_data
        return {}
