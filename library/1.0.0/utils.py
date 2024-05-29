import ipaddress
import secrets
import sys
import re


class TemplateException(Exception):
    pass


def throw_error(message):
    # When throwing a known error, hide the traceback
    # This is because the error is also shown in the UI
    # and having a traceback makes it hard for user to read
    sys.tracebacklimit = 0
    raise TemplateException(message)


def secure_string(length):
    return secrets.token_urlsafe(length)


def must_valid_range(range: str, msg: str = "") -> str:
    """
    Validates if the given range is a valid IP network range.
    If its valid, returns the range.
    If its not valid, throws an error.
    """
    try:
        ipaddress.ip_network(range)
        return range
    except ValueError:
        throw_error(msg or f"Expected range [{range}] to be a valid IP network range")


def must_valid_mac(mac: str, msg: str = "") -> str:
    """
    Validates if the given MAC address is valid.
    If its valid, returns the MAC address.
    If its not valid, throws an error.
    """
    re_mac_part = r"^[0-9a-fA-F]{2}$"
    parts = mac.split(":")
    if len(parts) != 6:
        throw_error(msg or f"Expected MAC address [{mac}] to be a valid MAC address")
    for part in parts:
        if not re.match(re_mac_part, part):
            throw_error(msg or f"Expected MAC address [{mac}] to be a valid MAC address")
    return mac


def must_valid_ip(ip: str, msg: str = "") -> str:
    """
    Validates if the given IP address is valid.
    If its valid, returns the IP address.
    If its not valid, throws an error.
    """
    try:
        ipaddress.ip_address(ip)
        return ip
    except ValueError:
        throw_error(msg or f"Expected IP address [{ip}] to be a valid IP address")


def must_valid_path(path: str) -> str:
    """
    Validates if the given path is valid.
    If its valid, returns the path.
    If its not valid, throws an error.
    """
    if not path.startswith("/"):
        throw_error(f"Expected path [{path}] to start with [/]")

    return path


def must_valid_port(port: int) -> int:
    """
    Validates if the given port is valid.
    If its valid, returns the port.
    If its not valid, throws an error.
    """
    if port < 1 or port > 65535:
        throw_error(f"Expected port [{port}] to be between 1 and 65535")

    return port
