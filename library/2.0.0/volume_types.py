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


class NfsVolume:
    def __init__(self, render_instance: "Render", config: dict):
        self._render_instance = render_instance

        if not config:
            raise RenderError("Expected [nfs_config] to be set for [nfs] type")

        required_keys = ["server", "path"]
        for key in required_keys:
            if not config.get(key):
                raise RenderError(f"Expected [{key}] to be set for [nfs] type")

        opts = [f"addr={config['server']}"]
        if config.get("options"):
            if not isinstance(config["options"], list):
                raise RenderError("Expected [nfs_config.options] to be a list for [nfs] type")

            tracked_keys: set[str] = set()
            disallowed_opts = ["addr"]
            for opt in config["options"]:
                if not isinstance(opt, str):
                    raise RenderError("Options for [nfs] type must be a list of strings.")

                key = opt.split("=")[0]
                if key in tracked_keys:
                    raise RenderError(f"Option [{key}] already added for [nfs] type.")
                if key in disallowed_opts:
                    raise RenderError(f"Option [{key}] is not allowed for [nfs] type.")
                opts.append(opt)
                tracked_keys.add(key)

        opts.sort()

        path = valid_fs_path_or_raise(config["path"].rstrip("/"))
        self.volume_spec = {
            "driver_opts": {
                "type": "nfs",
                "device": f":{path}",
                "o": f"{','.join([escape_dollar(opt) for opt in opts])}",
            },
        }

    def get(self):
        return self.volume_spec


class CifsVolume:
    def __init__(self, render_instance: "Render", config: dict):
        self._render_instance = render_instance
        self.volume_spec: dict = {}

        if not config:
            raise RenderError("Expected [cifs_config] to be set for [cifs] type")

        required_keys = ["server", "path", "username", "password"]
        for key in required_keys:
            if not config.get(key):
                raise RenderError(f"Expected [{key}] to be set for [cifs] type")

        opts = [
            f"user={config['username']}",
            f"password={config['password']}",
        ]

        if config.get("domain"):
            opts.append(f'domain={config["domain"]}')

        if config.get("options"):
            if not isinstance(config["options"], list):
                raise RenderError("Expected [cifs_config.options] to be a list for [cifs] type")

            tracked_keys: set[str] = set()
            disallowed_opts = ["user", "password", "domain"]
            for opt in config["options"]:
                if not isinstance(opt, str):
                    raise RenderError("Options for [cifs] type must be a list of strings.")

                key = opt.split("=")[0]
                if key in tracked_keys:
                    raise RenderError(f"Option [{key}] already added for [cifs] type.")
                if key in disallowed_opts:
                    raise RenderError(f"Option [{key}] is not allowed for [cifs] type.")
                for disallowed in disallowed_opts:
                    if key == disallowed:
                        raise RenderError(f"Option [{key}] is not allowed for [cifs] type.")
                opts.append(opt)
                tracked_keys.add(key)
        opts.sort()

        server = config["server"].lstrip("/")
        path = config["path"].strip("/")
        path = valid_fs_path_or_raise("/" + path).lstrip("/")

        self.volume_spec = {
            "driver_opts": {
                "type": "cifs",
                "device": f"//{server}/{path}",
                "o": f"{','.join([escape_dollar(opt) for opt in opts])}",
            },
        }

    def get(self):
        return self.volume_spec


class DockerVolume:
    def __init__(self, render_instance: "Render", config: dict):
        self._render_instance = render_instance
        self.volume_spec: dict = {}

    def get(self):
        return self.volume_spec