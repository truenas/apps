from . import utils


def get_port(port={}):
    req_keys = ["target", "published"]
    for key in req_keys:
        if key not in port:
            utils.throw_error(f"Port requires a [{key}] key to be set")

    return {
        "target": port["target"],
        "published": port["published"],
        "protocol": port.get("protocol", "tcp"),
        "mode": port.get("mode", "ingress"),
        "host_ip": port.get("host_ip", "0.0.0.0"),
    }
