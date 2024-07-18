import ipaddress

from . import utils


def must_valid_port(num: int):
    if num < 1 or num > 65535:
        utils.throw_error(f"Expected a valid port number, got [{num}]")


def must_valid_ip(ip: str):
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        utils.throw_error(f"Expected a valid IP address, got [{ip}]")


def must_valid_protocol(protocol: str):
    if protocol not in ["tcp", "udp"]:
        utils.throw_error(f"Expected a valid protocol, got [{protocol}]")


def must_valid_mode(mode: str):
    if mode not in ["ingress", "host"]:
        utils.throw_error(f"Expected a valid mode, got [{mode}]")


def get_port(port=None):
    port = port or {}
    must_valid_port(port["published"])
    must_valid_port(port["target"])
    must_valid_ip(port.get("host_ip", "0.0.0.0"))
    must_valid_protocol(port.get("protocol", "tcp"))
    must_valid_mode(port.get("mode", "ingress"))

    return {
        "target": port["target"],
        "published": port["published"],
        "protocol": port.get("protocol", "tcp"),
        "mode": port.get("mode", "ingress"),
        "host_ip": port.get("host_ip", "0.0.0.0"),
    }
