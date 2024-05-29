from . import configs
from . import networks
from . import volumes
from . import containers


def spec(values={}):

    return {
        "configs": configs.render_configs(values),
        "networks": networks.render_networks(values),
        "volumes": volumes.render_volumes(values),
        "services": containers.render_containers(values),
    }
