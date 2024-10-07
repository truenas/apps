from .error import RenderError
from .storage import Storage


class Container:

    def __init__(self, render_instance, name, image):
        self.render_instance = render_instance
        self.volume_mounts = []

        self.name = name
        self.image = self.resolve_image(image)

        self.tty = False
        self.stdin_open = False

    def add_volume(self, volume):  # FIXME: define what "volume" is
        storage = Storage(self.render_instance, volume)
        self.render_instance.add_volume(storage)
        self.volume_mounts.append(storage.volume_mount())

    def resolve_image(self, image):
        images = self.render_instance.values["images"]
        if image not in images:
            raise RenderError(f"Image [{image}] not found in values")
        repo = images[image].get("repository", "")
        tag = images[image].get("tag", "")

        if not repo:
            raise RenderError(f"Repository not found for image [{image}]")
        if not tag:
            raise RenderError(f"Tag not found for image [{image}]")

        return f"{repo}:{tag}"

    def set_tty(self, enabled=False):
        self.tty = enabled

    def set_stdin(self, enabled=False):
        self.stdin_open = enabled

    def render(self):
        result = {
            "image": self.image,
            "tty": self.tty,
            "stdin_open": self.stdin_open,
        }

        if self.volume_mounts:
            result["volume_mounts"] = self.volume_mounts

        return result
