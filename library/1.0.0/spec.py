from . import configs
from . import networks
from . import volumes


def spec(values={}):

    return {
        "configs": configs.render_configs(values),
        "networks": networks.render_networks(values),
        "volumes": volumes.render_volumes(values),
    }
