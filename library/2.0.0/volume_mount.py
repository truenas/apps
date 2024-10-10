try:
    from .error import RenderError
    from .volumes import Volumes, Volume
    from .validations import valid_host_path_propagation, valid_fs_path_or_raise
except ImportError:
    from error import RenderError
    from volumes import Volumes, Volume
    from validations import valid_host_path_propagation, valid_fs_path_or_raise


class VolumeMounts:
    # We need the volumes here, so we can get the config and other info
    def __init__(self, render_instance, volumes: Volumes):
        self._render_instance = render_instance
        self._volumes = volumes
        self._volume_mounts: list[VolumeMount] = []

    def add_volume_mount(self, vol_identifier: str, mount_path: str):
        mount_path = valid_fs_path_or_raise(mount_path.rstrip("/"))
        if vol_identifier not in self._volumes.volume_identifiers():
            raise RenderError(
                f"Volume [{vol_identifier}] not found in defined volumes. "
                f"Available volumes: [{', '.join(self._volumes.volume_identifiers())}]"
            )

        if self._target_exists(mount_path):
            raise RenderError(f"Container path [{mount_path}] already added")

        self._volume_mounts.append(
            VolumeMount(self._render_instance, mount_path, self._volumes.get_volume(vol_identifier))
        )

    def _target_exists(self, target: str):
        for mount in self._volume_mounts:
            if mount._spec["target"] == target:
                return True
        return False

    def has_mounts(self):
        return len(self._volume_mounts) > 0

    def render(self):
        return [v.render() for v in sorted(self._volume_mounts, key=lambda v: v._source)]


class VolumeMount:
    def __init__(self, render_instance, mount_path: str, vol: Volume):
        self._render_instance = render_instance
        self._source = vol.get_source()
        self._type = vol.get_vol_type_spec()

        read_only = vol.get_read_only()
        # Part of the spec that is not dependent on the volume type
        self._spec = {"type": self._type, "source": self._source, "target": mount_path, "read_only": read_only}

        vol_type_spec = self._mount_spec_mapping(self._type)(self._render_instance, vol)
        self._spec.update(vol_type_spec.render())

    def _mount_spec_mapping(self, type: str):
        mount_specs = {
            "bind": BindMount,
        }

        if type not in mount_specs:
            raise RenderError(
                f"Volume type [{type}] is not valid. Valid options are: [{', '.join(mount_specs.keys())}]"
            )

        return mount_specs[type]

    def render(self):
        return self._spec


class BindMount:
    def __init__(self, render_instance, vol: Volume):
        self._render_instance = render_instance
        self._vol: Volume = vol
        self._bind_spec: dict = {}

        config = vol.get_config()
        propagation = valid_host_path_propagation(config.get("propagation", "rprivate"))
        # Default to not creating the host path
        # But still allow manually setting create_host_path in the host_path_config (only available to app dev)
        create_host_path = config.get("create_host_path", False)
        self._bind_spec = {
            "bind": {
                "create_host_path": create_host_path,
                "propagation": propagation,
            }
        }

    def render(self):
        return self._bind_spec
