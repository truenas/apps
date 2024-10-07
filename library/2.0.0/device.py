try:
    from .validations import must_be_valid_path
except ImportError:
    from validations import must_be_valid_path


class Device:
    def __init__(self, host_device: str, container_device: str):
        must_be_valid_path(host_device)
        must_be_valid_path(container_device)
        self.host_device: str = host_device
        self.container_device: str = container_device

    def render(self):
        return f"{self.host_device}:{self.container_device}"
