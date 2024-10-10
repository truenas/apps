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

    def has_volumes(self) -> bool:
        """Check if there are any top-level volumes defined."""
        return any(v.is_top_level_volume() for v in self._volumes.values())

    def get_volume(self, identifier: str):
        """Retrieve a volume by its identifier."""
        if identifier not in self.volume_identifiers():
            raise RenderError(
                f"Volume [{identifier}] not found in defined volumes. "
                f"Available volumes: [{', '.join(self.volume_identifiers())}]"
            )
        return self._volumes[identifier]

    def volume_identifiers(self) -> list[str]:
        """List all volume identifiers."""
        return list(self._volumes.keys())

    def add_volume(self, identifier: str, config: dict):
        """Add a new volume with the given identifier and configuration."""
        if not identifier:
            raise RenderError("Volume name cannot be empty")
        if identifier in self._volumes:
            raise RenderError(f"Volume [{identifier}] already added.")

        self._volumes[identifier] = Volume(self._render_instance, identifier, config)

    def render(self) -> dict:
        """Render all top-level volumes into a dictionary."""
        return {v.get_name(): v.render() for v in self._volumes.values() if v.is_top_level_volume()}


class Volume:
    def __init__(self, render_instance, identifier: str, config: dict):
        self._render_instance = render_instance
        self._identifier = identifier
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
            "host_path": self._parse_host_path,
            "ix_volume": self._parse_ix_volume,
        }

        if vol_type not in vol_types:
            raise RenderError(
                f"Volume type [{vol_type}] is not valid. "
                f"Valid types are: [{', '.join(vol_types.keys())}] [{self._identifier}]"
            )

        return vol_types[vol_type]

    def _parse_host_path(self):
        if not self._raw_config.get("host_path_config"):
            raise RenderError(f"Expected [host_path_config] to be set for [host_path] type. [{self._identifier}]")
        hpc = self._raw_config["host_path_config"]
        if not hpc.get("path"):
            raise RenderError(f"Expected [host_path_config.path] to be set for [host_path] type. [{self._identifier}]")

        if hpc.get("acl_enable", False):
            acl = hpc.get("acl", {})
            if not acl.get("path"):
                raise RenderError(
                    f"Expected [host_path_config.acl.path] to be set for [host_path] type. [{self._identifier}]"
                )
            path = valid_fs_path_or_raise(acl["path"])
        else:
            path = valid_fs_path_or_raise(hpc["path"])

        self._volume_mount_type_spec = "bind"
        self._volume_source = path
        self._config = hpc
        self._volume_spec = None

    def _parse_ix_volume(self):
        ix_config = self._raw_config.get("ix_volume_config")
        if not ix_config:
            raise RenderError(f"Expected [ix_volume_config] to be set for [ix_volume] type. [{self._identifier}]")
        dataset_name = ix_config.get("dataset_name")
        if not dataset_name:
            raise RenderError(
                f"Expected [ix_volume_config.dataset_name] to be set for [ix_volume] type. [{self._identifier}]"
            )

        ix_volumes = self._render_instance.values.get("ix_volumes", {})
        if dataset_name not in ix_volumes:
            available = ", ".join(ix_volumes.keys())
            raise RenderError(
                f"Expected the key [{dataset_name}] to be set in [ix_volumes] for [ix_volume] type. "
                f"Available keys: [{available}]. [{self._identifier}]"
            )
        path = valid_fs_path_or_raise(ix_volumes[dataset_name].rstrip("/"))

        self._volume_mount_type_spec = "bind"
        self._volume_source = path
        self._config = ix_config
        self._volume_spec = None

    @property
    def source(self) -> str:
        return self._volume_source

    @property
    def mount_type(self) -> str:
        return self._volume_mount_type_spec

    @property
    def read_only(self) -> bool:
        return self._raw_config.get("read_only", False)

    @property
    def config(self) -> dict:
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
