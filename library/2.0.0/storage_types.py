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


class StorageItemResult:
    def __init__(self, source: str | None, volume_spec: dict | None, mount_spec: dict):
        self.source: str | None = source
        self.volume_spec: dict | None = volume_spec
        self.mount_spec: dict = mount_spec


class TmpfsStorage:
    """Parses storage item with type tmpfs."""

    def __init__(self, render_instance: "Render", config: dict):
        self._render_instance = render_instance
        tmpfs_config = config.get("tmpfs_config", {})
        self.mount_spec = TmpfsMountType(self._render_instance, tmpfs_config).render()

    def render(self):
        return StorageItemResult(source=None, volume_spec=None, mount_spec=self.mount_spec)


class HostPathStorage:
    """Parses storage item with type host_path."""

    def __init__(self, render_instance: "Render", config: dict):
        self._render_instance = render_instance
        host_path_config = config.get("host_path_config", {})

        if not host_path_config:
            raise RenderError("Expected [host_path_config] to be set for [host_path] type.")
        self.mount_spec = BindMountType(self._render_instance, host_path_config).render()

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


class IxVolumeStorage:
    """Parses storage item with type ix_volume."""

    def __init__(self, render_instance: "Render", config: dict):
        self._render_instance = render_instance
        ix_volume_config = config.get("ix_volume_config", {})

        if not ix_volume_config:
            raise RenderError("Expected [ix_volume_config] to be set for [ix_volume] type.")
        self.mount_spec = BindMountType(self._render_instance, ix_volume_config).render()

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


class DockerVolumeStorage:
    """Parses storage item with type volume."""

    def __init__(self, render_instance: "Render", config: dict):
        self._render_instance = render_instance
        volume_config = config.get("volume_config", {})

        if not volume_config:
            raise RenderError("Expected [volume_config] to be set for [volume] type.")
        self.mount_spec = VolumeMountType(self._render_instance, volume_config).render()

        volume_name = volume_config.get("volume_name")
        if not volume_name:
            raise RenderError("Expected [volume_config.volume_name] to be set for [volume] type.")

        # Top level docker volumes dont have a config, but need an empty dict
        self.volume_spec = {}
        self.source = volume_name

    def render(self):
        return StorageItemResult(source=self.source, volume_spec=self.volume_spec, mount_spec=self.mount_spec)


class AnonymousVolumeStorage:
    """Parses storage item with type anonymous."""

    def __init__(self, render_instance: "Render", config: dict):
        self._render_instance = render_instance
        volume_config = config.get("volume_config", {}) or {}
        self.mount_spec = VolumeMountType(self._render_instance, volume_config).render()

    def render(self):
        # Anonymous volumes do not have a top level definition
        return StorageItemResult(source=None, volume_spec=None, mount_spec=self.mount_spec)


class CifsStorage:
    """Parses storage item with type cifs."""

    def __init__(self, render_instance: "Render", config: dict):
        self._render_instance = render_instance
        cifs_config = config.get("cifs_config", {})

        if not cifs_config:
            raise RenderError("Expected [cifs_config] to be set for [cifs] type.")
        self.mount_spec = VolumeMountType(self._render_instance, cifs_config).render()

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


class NfsStorage:
    """Parses storage item with type nfs."""

    def __init__(self, render_instance: "Render", config: dict):
        self._render_instance = render_instance
        nfs_config = config.get("nfs_config", {})

        if not nfs_config:
            raise RenderError("Expected [nfs_config] to be set for [nfs] type.")
        self.mount_spec = VolumeMountType(self._render_instance, nfs_config).render()

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
