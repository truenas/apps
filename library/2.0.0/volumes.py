try:
    from .error import RenderError
    from .validations import valid_fs_path_or_raise
except ImportError:
    from error import RenderError
    from validations import valid_fs_path_or_raise


class Volumes:
    def __init__(self, render_instance):
        self._render_instance = render_instance
        self._volumes: dict[str, Volume] = {}

    def has_volumes(self):
        for v in self._volumes.values():
            if v.is_top_level_volume():
                return True
        return

    def get_volume(self, identifier: str):
        if identifier not in self.volume_identifiers():
            raise RenderError(
                f"Volume [{identifier}] not found in defined volumes. "
                f"Available volumes: [{', '.join(self.volume_identifiers())}]"
            )
        return self._volumes[identifier]

    def volume_identifiers(self):
        return self._volumes.keys()

    def add_volume(self, identifier: str, config: dict):
        if identifier == "":
            raise RenderError("Volume name cannot be empty")
        if identifier in self._volumes.keys():
            raise RenderError(f"Volume [{identifier}] already added")

        self._volumes[identifier] = Volume(identifier, config)

    def render(self):
        result: dict = {}
        for v in self._volumes.values():
            if v.is_top_level_volume():
                result[v.get_name()] = v.render()
        pass


class Volume:
    def __init__(self, identifier: str, config: dict):
        self._generated_name: str = ""  # remove?

        # The full/raw config passed to the volume
        self._raw_config: dict = config

        # The config relevant to the volume type
        self._config: dict = {}

        # Docker's top level volume spec
        self._volume_spec: dict | None = None
        # Docker's volume mount spec type
        self._volume_mount_type_spec: str = ""
        # Volume name for volumes or path for bind mounts
        self._volume_source: str = ""

        self._create_volume(identifier, config)

    def _create_volume(self, identifier: str, config: dict):
        vol_type = config.get("type", "")
        self._volume_type_processor_mapping(vol_type)()

    def _volume_type_processor_mapping(self, vol_type: str):
        vol_types = {
            "host_path": self._host_path_parser,
        }

        if vol_type not in vol_types:
            raise RenderError(
                f"Volume type [{vol_type}] is not valid. Valid options are: [{', '.join(vol_types.keys())}]"
            )

        return vol_types[vol_type]

    def _host_path_parser(self):
        if not self._raw_config.get("host_path_config"):
            raise RenderError("Expected [host_path_config] to be set for [host_path] type")
        if not self._raw_config["host_path_config"].get("path"):
            raise RenderError("Expected [host_path_config.path] to be set for [host_path] type")
        path = valid_fs_path_or_raise(self._raw_config["host_path_config"]["path"])

        self._volume_mount_type_spec = "bind"
        self._volume_source = path
        self._config = self._raw_config.get("host_path_config", {})
        self._volume_spec = None

    def get_read_only(self):
        return self._raw_config.get("read_only", False)

    def get_vol_type_spec(self):
        print("t", self._volume_mount_type_spec)
        return self._volume_mount_type_spec

    def get_source(self):
        return self._volume_source

    def get_config(self):
        return self._config

    # Not all volumes need to be defined
    # in the top level volumes section
    def is_top_level_volume(self):
        return self._volume_spec is not None

    def get_name(self):
        return self._generated_name

    def render(self):
        if self.is_top_level_volume():
            return self._volume_spec
        return {}
