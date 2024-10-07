try:
    from .error import RenderError
except ImportError:
    from error import RenderError


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
        if mode[7:] not in containers:
            raise RenderError(f"Service [{mode[7:]}] not found")
        return True

    raise RenderError(
        f"Invalid network mode [{mode}]. "
        f"Valid options are: [{', '.join(valid_modes)}] "
        f"or [service:<name>]"
    )


def must_be_valid_restart_policy(policy: str):
    valid_restart_policies = ("always", "on-failure", "unless-stopped", "no")
    if policy not in valid_restart_policies:
        raise RenderError(
            f"Restart policy [{policy}] is not valid. "
            f"Valid options are: [{', '.join(valid_restart_policies)}]"
        )


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
        raise RenderError(
            f"Capability [{cap}] is not valid. "
            f"Valid options are: [{', '.join(valid_policies)}]"
        )
