from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from render import Render

try:
    from .error import RenderError
    from .formatter import escape_dollar, get_hashed_name_for_volume
    from .mount_types import BindMountType, VolumeMountType, TmpfsMountType
    from .validations import valid_fs_path_or_raise
except ImportError:
    from error import RenderError
    from formatter import escape_dollar, get_hashed_name_for_volume
    from mount_types import BindMountType, VolumeMountType, TmpfsMountType
    from validations import valid_fs_path_or_raise


def merge_dicts_no_overwrite(dict1, dict2):
    overlapping_keys = dict1.keys() & dict2.keys()
    if overlapping_keys:
        raise ValueError(f"Merging of dicts failed. Overlapping keys: {overlapping_keys}")
    return {**dict1, **dict2}


class VolumeMounts:
    def __init__(self, render_instance: "Render"):
        self._render_instance = render_instance
        self._volume_mounts: set[VolumeMount] = set()

    def add_volume_mount(self, mount_path: str, config: dict):
        mount_path = valid_fs_path_or_raise(mount_path)
        if mount_path in [m.mount_path for m in self._volume_mounts]:
            raise RenderError(f"Mount path [{mount_path}] already used for another volume mount")

        volume_mount = VolumeMount(self._render_instance, mount_path, config)
        self._volume_mounts.add(volume_mount)

    def has_mounts(self) -> bool:
        return bool(self._volume_mounts)

    def render(self):
        return [vm.render() for vm in sorted(self._volume_mounts, key=lambda vm: vm.mount_path)]


class VolumeMount:
    # TODO: create a type for config
    def __init__(self, render_instance: "Render", mount_path: str, config: dict):
        self._render_instance = render_instance
        self.mount_path: str = mount_path
        self.read_only: bool = config.get("read_only", False)

        self.source: str | None = None  # tmpfs does not have a source
        self.spec_type: str = ""

        self.spec_config_for_type: dict = {}

        self.volume_mount_spec: dict = {}

        _type_spec_mapping = {
            "host_path": {"class": HostPathIxStorage, "spec_type": "bind"},
            "ix_volume": {"class": IxVolumeIxStorage, "spec_type": "bind"},
            "tmpfs": {"class": TmpfsIxStorage, "spec_type": "tmpfs"},
            "cifs": {"class": CifsIxStorage, "spec_type": "volume"},
            "nfs": {"class": NfsIxStorage, "spec_type": "volume"},
            # TODO: anonymous/temporary volumes
        }

        vol_type = config.get("type", None)
        if vol_type not in _type_spec_mapping:
            valid_types = ", ".join(_type_spec_mapping.keys())
            raise RenderError(f"Volume type [{vol_type}] is not valid. Valid options are: [{valid_types}]")

        # Fetch the class for the type
        vol_spec_class = _type_spec_mapping[vol_type]["class"]

        # Set the type in the mount type for the spec
        self.spec_type = _type_spec_mapping[vol_type]["spec_type"]

        # Parse the config for the type
        storage_item = vol_spec_class(self._render_instance, config).render()

        # Make sure source is not empty for all but tmpfs
        if self.spec_type != "tmpfs":
            if not storage_item.source:
                raise RenderError(f"Missing source for volume type [{vol_type}]")

        # Fetch the source (path for bind, volume name for volume)
        self.source = storage_item.source
        # Fetch the type specific config for the mount spec
        self.spec_config_for_type = storage_item.mount_spec

        if self.spec_type == "volume":
            # TODO: self._render_instance.add_volume...
            self._render_instance.new_volumes[self.source] = storage_item.volume_spec

    def render(self) -> dict:
        result = {
            "type": self.spec_type,
            "target": self.mount_path,
            "read_only": self.read_only,
        }

        if self.source is not None:
            result["source"] = self.source

        if self.spec_config_for_type:
            result = merge_dicts_no_overwrite(result, self.spec_config_for_type)

        return result


class StorageItemResult:
    def __init__(self, source: str | None, volume_spec: dict | None, mount_spec: dict):
        self.source: str | None = source
        self.volume_spec: dict | None = volume_spec
        self.mount_spec: dict = mount_spec


class TmpfsIxStorage:
    def __init__(self, render_instance: "Render", config: dict):
        self._render_instance = render_instance
        tmpfs_config = config.get("tmpfs_config", {})
        self.mount_spec = TmpfsMountType(self._render_instance, tmpfs_config).render()

    def render(self):
        return StorageItemResult(source=None, volume_spec=None, mount_spec=self.mount_spec)


class HostPathIxStorage:
    def __init__(self, render_instance: "Render", config: dict):
        self._render_instance = render_instance
        host_path_config = config.get("host_path_config", {})
        self.mount_spec = BindMountType(self._render_instance, host_path_config).render()

        if not host_path_config:
            raise RenderError("Expected [host_path_config] to be set for [host_path] type.")

        path = ""
        if host_path_config.get("acl_enable", False):
            acl = host_path_config.get("acl", {})
            if not acl.get("path"):
                raise RenderError("Expected [host_path_config.acl.path] to be set for [host_path] type.")
            path = valid_fs_path_or_raise(acl["path"])
        else:
            path = valid_fs_path_or_raise(host_path_config["path"])

        self.source = path.rstrip("/")

    def render(self):
        return StorageItemResult(source=self.source, volume_spec=None, mount_spec=self.mount_spec)


class IxVolumeIxStorage:
    def __init__(self, render_instance: "Render", config: dict):
        self._render_instance = render_instance
        ix_volume_config = config.get("ix_volume_config", {})
        self.mount_spec = BindMountType(self._render_instance, ix_volume_config).render()

        if not ix_volume_config:
            raise RenderError("Expected [ix_volume_config] to be set for [ix_volume] type.")

        dataset_name = ix_volume_config.get("dataset_name")
        if not dataset_name:
            raise RenderError("Expected [ix_volume_config.dataset_name] to be set for [ix_volume] type.")

        ix_volumes = self._render_instance.values.get("ix_volumes", {})
        if dataset_name not in ix_volumes:
            available = ", ".join(ix_volumes.keys())
            raise RenderError(
                f"Expected the key [{dataset_name}] to be set in [ix_volumes] for [ix_volume] type. "
                f"Available keys: [{available}]."
            )

        path = valid_fs_path_or_raise(ix_volumes[dataset_name].rstrip("/"))

        self.source = path

    def render(self):
        return StorageItemResult(source=self.source, volume_spec=None, mount_spec=self.mount_spec)


class CifsIxStorage:
    def __init__(self, render_instance: "Render", config: dict):
        self._render_instance = render_instance
        cifs_config = config.get("cifs_config", {})

        self.mount_spec = VolumeMountType(self._render_instance, cifs_config).render()
        if not cifs_config:
            raise RenderError("Expected [cifs_config] to be set for [cifs] type.")

        required_keys = ["server", "path", "username", "password"]
        for key in required_keys:
            if not cifs_config.get(key):
                raise RenderError(f"Expected [{key}] to be set for [cifs] type.")

        opts = [
            f"user={cifs_config['username']}",
            f"password={cifs_config['password']}",
        ]

        if cifs_config.get("domain"):
            opts.append(f'domain={cifs_config["domain"]}')

        if cifs_config.get("options"):
            if not isinstance(cifs_config["options"], list):
                raise RenderError("Expected [cifs_config.options] to be a list for [cifs] type.")
            tracked_keys: set[str] = set()
            disallowed_opts = ["user", "password", "domain"]
            for opt in cifs_config["options"]:
                if not isinstance(opt, str):
                    raise RenderError("Options for [cifs] type must be a list of strings.")
                key = opt.split("=")[0]
                if key in tracked_keys:
                    raise RenderError(f"Option [{key}] already added for [cifs] type.")
                if key in disallowed_opts:
                    raise RenderError(f"Option [{key}] is not allowed for [cifs] type.")
                opts.append(opt)
                tracked_keys.add(key)
        server = cifs_config["server"].lstrip("/")
        path = cifs_config["path"].strip("/")
        path = valid_fs_path_or_raise("/" + path).lstrip("/")

        # TODO: probably include the target here as well.
        # Reason is: what if we want multiple cifs with the same config, but mounted on different targets?
        self.source = get_hashed_name_for_volume("cifs", cifs_config)
        self.volume_spec = {
            "driver_opts": {
                "type": "cifs",
                "device": f"//{server}/{path}",
                "o": f"{','.join([escape_dollar(opt) for opt in opts])}",
            }
        }

    def render(self):
        return StorageItemResult(source=self.source, volume_spec=self.volume_spec, mount_spec=self.mount_spec)


class NfsIxStorage:
    def __init__(self, render_instance: "Render", config: dict):
        self._render_instance = render_instance
        nfs_config = config.get("nfs_config", {})

        self.mount_spec = VolumeMountType(self._render_instance, nfs_config).render()
        if not nfs_config:
            raise RenderError("Expected [nfs_config] to be set for [nfs] type.")

        required_keys = ["server", "path"]
        for key in required_keys:
            if not nfs_config.get(key):
                raise RenderError(f"Expected [{key}] to be set for [nfs] type.")

        opts = [f"addr={nfs_config['server']}"]
        if nfs_config.get("options"):
            if not isinstance(nfs_config["options"], list):
                raise RenderError("Expected [nfs_config.options] to be a list for [nfs] type.")

            tracked_keys: set[str] = set()
            disallowed_opts = ["addr"]
            for opt in nfs_config["options"]:
                if not isinstance(opt, str):
                    raise RenderError("Options for [nfs] type must be a list of strings.")
                key = opt.split("=")[0]
                if key in tracked_keys:
                    raise RenderError(f"Option [{key}] already added for [nfs] type.")
                if key in disallowed_opts:
                    raise RenderError(f"Option [{key}] is not allowed for [nfs] type.")
                opts.append(opt)
                tracked_keys.add(key)

        path = valid_fs_path_or_raise(nfs_config["path"].rstrip("/"))
        self.source = get_hashed_name_for_volume("nfs", nfs_config)
        self.volume_spec = {
            "driver_opts": {
                "type": "nfs",
                "device": f":{path}",
                "o": f"{','.join([escape_dollar(opt) for opt in opts])}",
            },
        }

    def render(self):
        return StorageItemResult(source=self.source, volume_spec=self.volume_spec, mount_spec=self.mount_spec)
