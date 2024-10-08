import ipaddress

try:
    from .error import RenderError
except ImportError:
    from error import RenderError


def must_be_valid_portal_scheme(scheme: str):
    schemes = ("http", "https")
    if scheme not in schemes:
        raise RenderError(f"Portal Scheme [{scheme}] is not valid. Valid options are: [{', '.join(schemes)}]")


def must_be_valid_port(port: int):
    if port < 1 or port > 65535:
        raise RenderError(f"Invalid port [{port}]. Valid ports are between 1 and 65535")


def must_be_valid_ip(ip: str):
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        raise RenderError(f"Invalid IP address [{ip}]")


def must_be_valid_port_mode(mode: str):
    modes = ("ingress", "host")
    if mode not in modes:
        raise RenderError(f"Port Mode [{mode}] is not valid. Valid options are: [{', '.join(modes)}]")


def must_be_valid_port_protocol(protocol: str):
    protocols = ("tcp", "udp")
    if protocol not in protocols:
        raise RenderError(f"Port Protocol [{protocol}] is not valid. Valid options are: [{', '.join(protocols)}]")


def must_be_valid_depend_condition(condition: str):
    valid_conditions = ("service_started", "service_healthy", "service_completed_successfully")
    if condition not in valid_conditions:
        raise RenderError(
            f"Depend Condition [{condition}] is not valid. Valid options are: [{', '.join(valid_conditions)}]"
        )


def must_be_valid_cgroup_perm(cgroup_perm: str):
    valid_cgroup_perms = ("r", "w", "m", "rw", "rm", "wm", "rwm")
    if cgroup_perm not in valid_cgroup_perms:
        raise RenderError(
            f"Cgroup Permission [{cgroup_perm}] is not valid. Valid options are: [{', '.join(valid_cgroup_perms)}]"
        )


def must_not_be_disallowed_dns_opt(dns_opt: str):
    disallowed_dns_opts = []
    if dns_opt in disallowed_dns_opts:
        raise RenderError(f"DNS Option [{dns_opt}] is not allowed to added.")


def must_be_valid_path(path: str):
    if not path.startswith("/"):
        raise RenderError(f"Path [{path}] must start with /")


def must_not_be_disallowed_device(path: str):
    disallowed_devices = ["/dev/dri"]
    if path in disallowed_devices:
        raise RenderError(f"Device [{path}] is not allowed to be manually added.")


def must_be_valid_network_mode(mode: str, containers: list[str]):
    valid_modes = ("host", "none")
    if mode in valid_modes:
        return True

    if mode.startswith("service:"):
        if mode[8:] not in containers:
            raise RenderError(f"Service [{mode[8:]}] not found")
        return True

    raise RenderError(
        f"Invalid network mode [{mode}]. Valid options are: [{', '.join(valid_modes)}] or [service:<name>]"
    )


def must_be_valid_restart_policy(policy: str, maximum_retry_count: int = 0):
    valid_restart_policies = ("always", "on-failure", "unless-stopped", "no")
    if policy not in valid_restart_policies:
        raise RenderError(
            f"Restart policy [{policy}] is not valid. Valid options are: [{', '.join(valid_restart_policies)}]"
        )
    if policy != "on-failure" and maximum_retry_count != 0:
        raise RenderError("Maximum retry count can only be set for [on-failure] restart policy")

    if maximum_retry_count < 0:
        raise RenderError("Maximum retry count must be a positive integer")


def must_be_valid_cap(cap: str):
    valid_policies = (
        "ALL",
        "AUDIT_CONTROL",
        "AUDIT_READ",
        "AUDIT_WRITE",
        "BLOCK_SUSPEND",
        "BPF",
        "CHECKPOINT_RESTORE",
        "SYS_ADMIN",
        "CHOWN",
        "DAC_OVERRIDE",
        "DAC_READ_SEARCH",
        "FOWNER",
        "DAC_READ_SEARCH",
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
        "SYS_ADMIN",
        "SETGID",
        "SETFCAP",
        "SETPCAP",
        "SETPCAP",
        "SETUID",
        "SYS_ADMIN",
        "BPF",
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
