import os
import sys
import yaml
import subprocess

CONTAINER_IMAGE = "ghcr.io/truenas/apps_validation:latest"
PLATFORM = "linux/amd64"


def cap_description_map(cap: str, services: list[str]):
    data = {
        "AUDIT_CONTROL": "able to control audit subsystem configuration",
        "AUDIT_READ": "able to read audit log entries",
        "AUDIT_WRITE": "able to write records to audit log",
        "BLOCK_SUSPEND": "able to block system suspend operations",
        "BPF": "able to use Berkeley Packet Filter programs",
        "CHECKPOINT_RESTORE": "able to use checkpoint/restore functionality",
        "CHOWN": "able to change file ownership arbitrarily",
        "DAC_OVERRIDE": "able to bypass file permission checks",
        "DAC_READ_SEARCH": "able to bypass read/execute permission checks",
        "FOWNER": "able to bypass permission checks for file operations",
        "FSETID": "able to preserve set-user-ID and set-group-ID bits",
        "IPC_LOCK": "able to lock memory segments in RAM",
        "IPC_OWNER": "able to bypass permission checks for IPC operations",
        "KILL": "able to send signals to any process",
        "LEASE": "able to establish file leases",
        "LINUX_IMMUTABLE": "able to set immutable and append-only file attributes",
        "MAC_ADMIN": "able to configure Mandatory Access Control",
        "MAC_OVERRIDE": "able to override Mandatory Access Control restrictions",
        "MKNOD": "able to create special files using mknod()",
        "NET_ADMIN": "able to perform network administration tasks",
        "NET_BIND_SERVICE": "able to bind to privileged ports (< 1024)",
        "NET_BROADCAST": "able to make socket broadcasts",
        "NET_RAW": "able to use raw and packet sockets",
        "PERFMON": "able to access performance monitoring interfaces",
        "SETFCAP": "able to set file capabilities on other files",
        "SETGID": "able to change group ID of processes",
        "SETPCAP": "able to transfer capabilities between processes",
        "SETUID": "able to change user ID of processes",
        "SYS_ADMIN": "able to perform system administration operations",
        "SYS_BOOT": "able to reboot and load/unload kernel modules",
        "SYS_CHROOT": "able to use chroot() system call",
        "SYS_MODULE": "able to load and unload kernel modules",
        "SYS_NICE": "able to modify process scheduling priority",
        "SYS_PACCT": "able to configure process accounting",
        "SYS_PTRACE": "able to trace and control other processes",
        "SYS_RAWIO": "able to perform raw I/O operations",
        "SYS_RESOURCE": "able to override resource limits",
        "SYS_TIME": "able to set system clock and real-time clock",
        "SYS_TTY_CONFIG": "able to configure TTY devices",
        "SYSLOG": "able to perform privileged syslog operations",
        "WAKE_ALARM": "able to trigger system wake alarms",
    }

    if cap not in data:
        raise Exception(f"Cap [{cap}] not found")
    if len(services) == 0:
        raise Exception(f"No services found for cap [{cap}]")

    services = [s.replace("-", " ").title() for s in services]

    if len(services) == 1:
        return f"{services[0].title()} is {data[cap]}"
    return f"{', '.join(services)} are {data[cap]}"


def get_apps():
    apps = {}
    for train in os.listdir("ix-dev"):
        for app in os.listdir(f"ix-dev/{train}"):
            if train == "test" and app in ("other-nginx", "nginx"):
                continue
            app_path = f"ix-dev/{train}/{app}"
            if not os.path.exists(os.path.join(app_path, "app.yaml")):
                continue

            test_values = []
            for test_file in os.listdir(os.path.join(app_path, "templates/test_values")):
                if test_file.endswith(".yaml"):
                    test_values.append(test_file)

            apps[app_path] = {"test_values": test_values}
    return apps


def get_caps_from_compose(compose):
    caps = {}
    for service in compose["services"]:
        data = compose["services"][service]
        # Ignore short-lived containers
        if not data.get("restart", ""):
            print(f"No restart found for {service} in {app_path}")
            continue
        if data["restart"].startswith("on-failure"):
            continue
        if "cap_add" in data:
            caps[service] = set(data["cap_add"])
    return caps


def bump_version(version: str):
    parts = version.split(".")
    parts[2] = str(int(parts[2]) + 1)
    return ".".join(parts)


def update_caps_for_app(app_path: str, app: dict):
    all_caps: dict[str, set[str]] = {}

    for test_file in app["test_values"]:
        cmd = " ".join(
            [
                f"docker run --platform {PLATFORM} --quiet --rm -v {os.getcwd()}:/workspace {CONTAINER_IMAGE}",
                "apps_render_app render",
                f"--path /workspace/{app_path}",
                f"--values /workspace/{app_path}/templates/test_values/{test_file}",
            ]
        )
        res = subprocess.run(cmd, shell=True, capture_output=True)
        if res.returncode != 0:
            print(res.stderr.decode("utf-8"))
            raise Exception(f"Failed to render {app_path}/{test_file}")
        with open(os.path.join(app_path, "templates/rendered/docker-compose.yaml"), "r") as f:
            out = yaml.safe_load(f)
            for service, caps in get_caps_from_compose(out).items():
                for cap in caps:
                    if cap not in all_caps:
                        all_caps[cap] = set()
                    all_caps[cap].add(service)

    capabilities = []
    print(f"Updating capabilities for {app_path}")
    for cap, services in all_caps.items():
        capabilities.append({"name": cap, "description": cap_description_map(cap, list(services))})
    capabilities = sorted(capabilities, key=lambda c: c["name"])
    with open(os.path.join(app_path, "app.yaml"), "r") as f:
        app = yaml.safe_load(f)
        if len(app["categories"]) > 1:
            print(f"WARNING: App [{app_path}] has more than one category")
        if app["capabilities"] != capabilities:
            app["version"] = bump_version(app["version"])
        app["capabilities"] = capabilities
        with open(os.path.join(app_path, "app.yaml"), "w") as f:
            yaml.dump(app, f)


if __name__ == "__main__":
    apps = get_apps()

    if len(sys.argv) > 2:
        train = sys.argv[1]
        app = sys.argv[2]
        key = f"ix-dev/{train}/{app}"
        if key not in apps:
            print(f"App [{key}] not found")
            sys.exit(1)
        update_caps_for_app(key, apps[key])
    else:
        for app_path, app in apps.items():
            update_caps_for_app(app_path, app)
