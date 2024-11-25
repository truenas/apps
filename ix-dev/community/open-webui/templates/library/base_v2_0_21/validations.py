import re
import ipaddress

try:
    from .error import RenderError
except ImportError:
    from error import RenderError

OCTAL_MODE_REGEX = re.compile(r"^0[0-7]{3}$")


def valid_redis_password_or_raise(password: str):
    forbidden_chars = [" ", "'"]
    for char in forbidden_chars:
        if char in password:
            raise RenderError(f"Redis password cannot contain [{char}]")


def valid_octal_mode_or_raise(mode: str):
    mode = str(mode)
    if not OCTAL_MODE_REGEX.match(mode):
        raise RenderError(f"Expected [mode] to be a octal string, got [{mode}]")
    return mode


def valid_host_path_propagation(propagation: str):
    valid_propagations = ("shared", "slave", "private", "rshared", "rslave", "rprivate")
    if propagation not in valid_propagations:
        raise RenderError(f"Expected [propagation] to be one of [{', '.join(valid_propagations)}], got [{propagation}]")
    return propagation


def valid_portal_scheme_or_raise(scheme: str):
    schemes = ("http", "https")
    if scheme not in schemes:
        raise RenderError(f"Portal Scheme [{scheme}] is not valid. Valid options are: [{', '.join(schemes)}]")
    return scheme


def valid_port_or_raise(port: int):
    if port < 1 or port > 65535:
        raise RenderError(f"Invalid port [{port}]. Valid ports are between 1 and 65535")
    return port


def valid_ip_or_raise(ip: str):
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        raise RenderError(f"Invalid IP address [{ip}]")
    return ip


def valid_port_mode_or_raise(mode: str):
    modes = ("ingress", "host")
    if mode not in modes:
        raise RenderError(f"Port Mode [{mode}] is not valid. Valid options are: [{', '.join(modes)}]")
    return mode


def valid_port_protocol_or_raise(protocol: str):
    protocols = ("tcp", "udp")
    if protocol not in protocols:
        raise RenderError(f"Port Protocol [{protocol}] is not valid. Valid options are: [{', '.join(protocols)}]")
    return protocol


def valid_depend_condition_or_raise(condition: str):
    valid_conditions = ("service_started", "service_healthy", "service_completed_successfully")
    if condition not in valid_conditions:
        raise RenderError(
            f"Depend Condition [{condition}] is not valid. Valid options are: [{', '.join(valid_conditions)}]"
        )
    return condition


def valid_cgroup_perm_or_raise(cgroup_perm: str):
    valid_cgroup_perms = ("r", "w", "m", "rw", "rm", "wm", "rwm", "")
    if cgroup_perm not in valid_cgroup_perms:
        raise RenderError(
            f"Cgroup Permission [{cgroup_perm}] is not valid. Valid options are: [{', '.join(valid_cgroup_perms)}]"
        )
    return cgroup_perm


def allowed_dns_opt_or_raise(dns_opt: str):
    disallowed_dns_opts = []
    if dns_opt in disallowed_dns_opts:
        raise RenderError(f"DNS Option [{dns_opt}] is not allowed to added.")
    return dns_opt


def valid_http_path_or_raise(path: str):
    path = _valid_path_or_raise(path)
    return path


def valid_fs_path_or_raise(path: str):
    # There is no reason to allow / as a path,
    # either on host or in a container side.
    if path == "/":
        raise RenderError(f"Path [{path}] cannot be [/]")
    path = _valid_path_or_raise(path)
    return path


def _valid_path_or_raise(path: str):
    if path == "":
        raise RenderError(f"Path [{path}] cannot be empty")
    if not path.startswith("/"):
        raise RenderError(f"Path [{path}] must start with /")
    if "//" in path:
        raise RenderError(f"Path [{path}] cannot contain [//]")
    return path


def allowed_device_or_raise(path: str):
    disallowed_devices = ["/dev/dri", "/dev/bus/usb"]
    if path in disallowed_devices:
        raise RenderError(f"Device [{path}] is not allowed to be manually added.")
    return path


def valid_network_mode_or_raise(mode: str, containers: list[str]):
    valid_modes = ("host", "none")
    if mode in valid_modes:
        return mode

    if mode.startswith("service:"):
        if mode[8:] not in containers:
            raise RenderError(f"Service [{mode[8:]}] not found")
        return mode

    raise RenderError(
        f"Invalid network mode [{mode}]. Valid options are: [{', '.join(valid_modes)}] or [service:<name>]"
    )


def valid_restart_policy_or_raise(policy: str, maximum_retry_count: int = 0):
    valid_restart_policies = ("always", "on-failure", "unless-stopped", "no")
    if policy not in valid_restart_policies:
        raise RenderError(
            f"Restart policy [{policy}] is not valid. Valid options are: [{', '.join(valid_restart_policies)}]"
        )
    if policy != "on-failure" and maximum_retry_count != 0:
        raise RenderError("Maximum retry count can only be set for [on-failure] restart policy")

    if maximum_retry_count < 0:
        raise RenderError("Maximum retry count must be a positive integer")

    return policy


def valid_cap_or_raise(cap: str):
    valid_policies = (
        "ALL",
        "AUDIT_CONTROL",
        "AUDIT_READ",
        "AUDIT_WRITE",
        "BLOCK_SUSPEND",
        "BPF",
        "CHECKPOINT_RESTORE",
        "CHOWN",
        "DAC_OVERRIDE",
        "DAC_READ_SEARCH",
        "FOWNER",
        "FSETID",
        "IPC_LOCK",
        "IPC_OWNER",
        "KILL",
        "LEASE",
        "LINUX_IMMUTABLE",
        "MAC_ADMIN",
        "MAC_OVERRIDE",
        "MKNOD",
        "NET_ADMIN",
        "NET_BIND_SERVICE",
        "NET_BROADCAST",
        "NET_RAW",
        "PERFMON",
        "SETFCAP",
        "SETGID",
        "SETPCAP",
        "SETUID",
        "SYS_ADMIN",
        "SYS_BOOT",
        "SYS_CHROOT",
        "SYS_MODULE",
        "SYS_NICE",
        "SYS_PACCT",
        "SYS_PTRACE",
        "SYS_RAWIO",
        "SYS_RESOURCE",
        "SYS_TIME",
        "SYS_TTY_CONFIG",
        "SYSLOG",
        "WAKE_ALARM",
    )

    if cap not in valid_policies:
        raise RenderError(f"Capability [{cap}] is not valid. " f"Valid options are: [{', '.join(valid_policies)}]")

    return cap
