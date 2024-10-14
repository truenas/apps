import json
import hashlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from render import Render

try:
    from .error import RenderError
    from .formatter import escape_dollar
    from .validations import valid_fs_path_or_raise
except ImportError:
    from error import RenderError
    from formatter import escape_dollar
    from validations import valid_fs_path_or_raise


class Volume:
    def __init__(self, render_instance: "Render", identifier: str, config: dict):
        self._render_instance = render_instance
        self._identifier: str = identifier

        """
        For some volumes like cifs or nfs, we need to generate a unique name for the volume,
        based on its configuration. Reason is that Docker does not update any volume after creation.
        This is to ensure that changing any value (eg server address) in the config will result in a new volume
        """
        self._generated_name: str = ""

        # The full/raw config passed to the volume
        self._raw_config: dict = config

        # The config relevant to the volume type
        self._config: dict = {}

        # Docker's top level volume spec
        self._volume_spec: dict | None = None
        # Docker's volume mount spec type
        self._volume_mount_type_spec: str = ""
        # Volume name for volumes or path for bind mounts
        self._volume_source: str | None = None

        self._create_volume(config)

    def _create_volume(self, config: dict):
        vol_type = config.get("type", "")
        self._volume_type_processor_mapping(vol_type)()

    def _volume_type_processor_mapping(self, vol_type: str):
        vol_types = {
            "host_path": self._parse_host_path,
            "ix_volume": self._parse_ix_volume,
            "tmpfs": self._parse_tmpfs,
            "cifs": self._parse_cifs,
            "nfs": self._parse_nfs,
        }

        if vol_type not in vol_types:
            raise RenderError(
                f"Volume type [{vol_type}] is not valid. Valid types are: [{', '.join(vol_types.keys())}]. "
                f"Got [{vol_type}]. [{self._identifier}]"
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

    def _parse_tmpfs(self):
        tmpfs_config = self._raw_config.get("tmpfs_config") or {}

        self._volume_mount_type_spec = "tmpfs"
        self._volume_source = None
        self._config = tmpfs_config
        self._volume_spec = None

    def _parse_cifs(self):
        cifs_config = self._raw_config.get("cifs_config")
        if not cifs_config:
            raise RenderError(f"Expected [cifs_config] to be set for [cifs] type. [{self._identifier}]")

        required_keys = ["server", "path", "username", "password"]
        for key in required_keys:
            if not cifs_config.get(key):
                raise RenderError(f"Expected [{key}] to be set for [cifs] type. [{self._identifier}]")
        opts = [
            f"user={cifs_config['username']}",
            f"password={cifs_config['password']}",
        ]

        if cifs_config.get("domain"):
            opts.append(f'domain={cifs_config["domain"]}')

        if cifs_config.get("options"):
            if not isinstance(cifs_config["options"], list):
                raise RenderError(f"Expected [cifs_config.options] to be a list for [cifs] type. [{self._identifier}]")
            tracked_keys: set[str] = set()
            disallowed_opts = ["user", "password", "domain"]
            for opt in cifs_config["options"]:
                if not isinstance(opt, str):
                    raise RenderError(f"Options for [cifs] type must be a list of strings. [{self._identifier}]")
                key = opt.split("=")[0]
                if key in tracked_keys:
                    raise RenderError(f"Option [{key}] already added for [cifs] type. [{self._identifier}]")
                if key in disallowed_opts:
                    raise RenderError(f"Option [{key}] is not allowed for [cifs] type. [{self._identifier}]")
                opts.append(opt)
                tracked_keys.add(key)

        server = cifs_config["server"].lstrip("/")
        path = cifs_config["path"].strip("/")
        path = valid_fs_path_or_raise("/" + path).lstrip("/")

        self._volume_mount_type_spec = "volume"
        self._config = cifs_config
        self._generated_name = get_hashed_name_for_volume(f"cifs_{self._identifier}", cifs_config)
        self._volume_source = self._generated_name
        self._volume_spec = {
            "driver_opts": {
                "type": "cifs",
                "device": f"//{server}/{path}",
                "o": f"{','.join([escape_dollar(opt) for opt in opts])}",
            },
        }

    def _parse_nfs(self):
        nfs_config = self._raw_config.get("nfs_config")
        if not nfs_config:
            raise RenderError(f"Expected [nfs_config] to be set for [nfs] type. [{self._identifier}]")

        required_keys = ["server", "path"]
        for key in required_keys:
            if not nfs_config.get(key):
                raise RenderError(f"Expected [{key}] to be set for [nfs] type. [{self._identifier}]")

        opts = [f"addr={nfs_config['server']}"]
        if nfs_config.get("options"):
            if not isinstance(nfs_config["options"], list):
                raise RenderError(f"Expected [nfs_config.options] to be a list for [nfs] type. [{self._identifier}]")

            tracked_keys: set[str] = set()
            disallowed_opts = ["addr"]
            for opt in nfs_config["options"]:
                if not isinstance(opt, str):
                    raise RenderError(f"Options for [nfs] type must be a list of strings. [{self._identifier}]")
                key = opt.split("=")[0]
                if key in tracked_keys:
                    raise RenderError(f"Option [{key}] already added for [nfs] type. [{self._identifier}]")
                if key in disallowed_opts:
                    raise RenderError(f"Option [{key}] is not allowed for [nfs] type. [{self._identifier}]")
                opts.append(opt)
                tracked_keys.add(key)

        path = valid_fs_path_or_raise(nfs_config["path"].rstrip("/"))

        self._volume_mount_type_spec = "volume"
        self._config = nfs_config
        self._generated_name = get_hashed_name_for_volume(f"nfs_{self._identifier}", nfs_config)
        self._volume_source = self._generated_name
        self._volume_spec = {
            "driver_opts": {
                "type": "nfs",
                "device": f":{path}",
                "o": f"{','.join([escape_dollar(opt) for opt in opts])}",
            },
        }

    def is_mounted(self) -> bool:
        """Check if the volume is mounted."""
        for c in self._render_instance._containers.values():
            for m in c.volume_mounts._volume_mounts:
                if m.source == self.source:
                    return True
        return False

    @property
    def name(self) -> str:
        """Return the name of the volume."""
        return self._generated_name or self._identifier

    @property
    def source(self) -> str:
        """
        Return the source path for bind mounts or volume name for volumes.
        If the volume is a temporary volume, returns empty string.
        """
        return self._volume_source or ""

    @property
    def mount_type(self) -> str:
        return self._volume_mount_type_spec

    @property
    def read_only(self) -> bool:
        return self._raw_config.get("read_only", False)

    @property
    def config(self) -> dict:
        return self._config

    @property
    def is_top_level_volume(self) -> bool:
        """Determine if the volume should be defined at the top level in Docker Compose."""
        return self._volume_spec is not None

    def render(self):
        if self.is_top_level_volume:
            return self._volume_spec
        return {}


def get_hashed_name_for_volume(prefix: str, config: dict):
    config_hash = hashlib.sha256(json.dumps(config).encode("utf-8")).hexdigest()
    return f"{prefix}_{config_hash}"
