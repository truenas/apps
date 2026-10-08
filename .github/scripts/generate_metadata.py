#!/usr/bin/env python3
"""
TrueNAS Apps metadata generator

Renders each app with every one of its test values and updates its app.yaml with the
capabilities and users (run_as_context) of the resulting containers. Also validates
parts of the app's questions.yaml, ix_values.yaml and app.yaml along the way.
"""

# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pyyaml",
# ]
# ///

import argparse
import logging
import os
import re
import shlex
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import yaml

CONTAINER_IMAGE = "ghcr.io/truenas/apps_validation:latest"
PLATFORM = "linux/amd64"

APPS_ROOT_DIR = Path("ix-dev")
TEST_VALUES_DIR = "templates/test_values"
RENDERED_COMPOSE_PATH = "templates/rendered/docker-compose.yaml"
APP_METADATA_FILE = "app.yaml"
APP_VALUES_FILE = "ix_values.yaml"
QUESTIONS_FILE = "questions.yaml"

# Special apps excluded from test train
EXCLUDED_TEST_APPS = {"other-nginx", "nginx"}

# Registries that garbage-collect manifests no longer referenced by a tag,
# so a digest pin (tag@sha256:...) breaks once the tag moves
NO_DIGEST_PIN_REGISTRIES = ("quay.io/",)

# libyaml-backed loader is much faster; fall back if PyYAML was built without it
YAML_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)

RE_VAR_NAME = re.compile(r"^[a-z0-9_]+$")
# Existing variable names that predate the naming rule
VAR_NAME_EXCEPTIONS = {
    "TZ",
    "storageEntry",
    "publicIpDnsProviderEntry",
    "jenkinsJavaOpt",
    "jenkinsOption",
    "aspellDict",
    "trustedProxy",
    "extraParam",
}

MEDIA_BASE_URL = "https://media.sys.truenas.net/apps"
MAINTAINERS = [{"email": "dev@truenas.com", "name": "truenas", "url": "https://www.truenas.com/"}]

# The default "apps" user/group, also used by apps that let the user pick the user to run as
APPS_ID = 568

CAPABILITY_DESCRIPTIONS = {
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

# Service names whose title can't be derived from the name itself
SERVICE_TITLES = {
    "dssystem": "DS System",
    "npm": "Nginx Proxy Manager",
    "npmplus": "Nginx Proxy Manager Plus",
    "omada": "Omada Controller",
    "lms": "Lyrion Media Server",
}

# Host ids that are the same user and group name
COMMON_ID_NAMES = {
    0: "root",
    1: "daemon",
    2: "bin",
    3: "sys",
    7: "lp",
    8: "mail",
    9: "news",
    10: "uucp",
    13: "proxy",
    33: "www-data",
    34: "backup",
    38: "list",
    39: "irc",
    41: "gnats",
    101: "systemd-timesync",
    568: "apps",
    666: "webdav",
    950: "truenas_admin",
    986: "libvirt-qemu",
    998: "polkitd",
}

USER_NAMES = {
    4: "sync",
    5: "games",
    6: "man",
    100: "_apt",
    102: "systemd-network",
    103: "systemd-resolve",
    104: "messagebus",
    105: "avahi",
    106: "_rpc",
    107: "statd",
    108: "consul",
    109: "nvpd",
    110: "nslcd",
    111: "sshd",
    112: "systemd-coredump",
    113: "Debian-snmp",
    114: "ntp",
    115: "Debian-exim",
    116: "tftp",
    117: "sssd",
    118: "tcpdump",
    120: "proftpd",
    121: "ftp",
    122: "nut",
    123: "dnsmasq",
    124: "ladvd",
    125: "nova",
    126: "haproxy",
    127: "uuidd",
    128: "ntpsec",
    129: "tss",
    130: "iperf3",
    131: "_chrony",
    999: "netdata",
    65534: "nobody",
    **COMMON_ID_NAMES,
}

GROUP_NAMES = {
    4: "adm",
    5: "tty",
    6: "disk",
    12: "man",
    14: "ftp",
    15: "kmem",
    20: "dialout",
    21: "fax",
    22: "voice",
    24: "cdrom",
    25: "floppy",
    26: "tape",
    27: "sudo",
    29: "audio",
    30: "dip",
    37: "operator",
    40: "src",
    42: "shadow",
    43: "utmp",
    44: "video",
    45: "sasl",
    46: "plugdev",
    50: "staff",
    60: "games",
    100: "users",
    102: "systemd-journal",
    103: "systemd-network",
    104: "systemd-resolve",
    105: "input",
    106: "kvm",
    107: "render",
    108: "crontab",
    109: "netdev",
    110: "ssh",
    111: "messagebus",
    112: "avahi",
    113: "consul",
    114: "nvpd",
    115: "nslcd",
    116: "systemd-coredump",
    117: "Debian-snmp",
    118: "ssl-cert",
    119: "ntp",
    120: "Debian-exim",
    121: "tftp",
    122: "sssd",
    123: "tcpdump",
    124: "rdma",
    126: "nut",
    127: "ladvd",
    128: "libvirt",
    129: "nova",
    130: "haproxy",
    131: "uuidd",
    132: "i2c",
    133: "sgx",
    134: "_ssh",
    135: "ntpsec",
    136: "tss",
    137: "iperf3",
    138: "_chrony",
    544: "builtin_administrators",
    545: "builtin_users",
    546: "builtin_guests",
    951: "truenas_readonly_administrators",
    952: "truenas_sharing_administrators",
    995: "incus-admin",
    996: "incus",
    997: "netdata",
    999: "docker",
    65534: "nogroup",
    **COMMON_ID_NAMES,
}

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class App:
    train: str
    name: str
    path: Path
    test_values: list[str]


@dataclass
class Analysis:
    """What an app's containers look like across all of its test values."""

    service_names: set[str]
    # capability -> services that add it
    capabilities: dict[str, set[str]]
    # service -> (uid, gid) of each test value
    users: dict[str, list[tuple[int, int]]]


def read_yaml(path: Path) -> dict:
    with open(path) as f:
        data = yaml.load(f, Loader=YAML_LOADER)
    if not isinstance(data, dict):
        raise ValueError(f"YAML file {path} must contain a dictionary at root level, got {type(data)}")
    return data


def write_yaml(path: Path, data: dict) -> None:
    with open(path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


# Discovery


def load_app(train: str, path: Path) -> App | None:
    if train == "test" and path.name in EXCLUDED_TEST_APPS:
        logger.debug(f"Skipping excluded test app: {path.name}")
        return None

    if not (path / APP_METADATA_FILE).exists():
        logger.warning(f"Skipping {path}: missing {APP_METADATA_FILE}")
        return None

    values_dir = path / TEST_VALUES_DIR
    test_values = []
    if values_dir.exists():
        test_values = sorted(f.name for f in values_dir.iterdir() if f.is_file() and f.suffix == ".yaml")

    return App(train=train, name=path.name, path=path, test_values=test_values)


def load_all_apps() -> list[App]:
    apps = []
    for train_path in sorted(APPS_ROOT_DIR.iterdir()):
        if not train_path.is_dir():
            continue
        logger.info(f"Scanning train: {train_path.name}")
        for app_path in sorted(train_path.iterdir()):
            if app_path.is_dir() and (app := load_app(train_path.name, app_path)):
                apps.append(app)

    logger.info(f"Discovered {len(apps)} apps total")
    return apps


# Rendering and analysis


def render(app: App, values_file: str) -> dict:
    """Render the app with the given test values and return the compose data."""
    values_path = app.path / TEST_VALUES_DIR / values_file
    compose_path = app.path / RENDERED_COMPOSE_PATH

    # Render and make the (root owned) rendered file readable in a single container
    render_cmd = shlex.join(
        ["apps_render_app", "render", f"--path=/workspace/{app.path}", f"--values=/workspace/{values_path}"]
    )
    chmod_cmd = shlex.join(["chmod", "777", f"/workspace/{compose_path}"])
    docker_cmd = [
        "docker",
        "run",
        f"--platform={PLATFORM}",
        "--quiet",
        "--rm",
        "-e",
        "FAKE_ENV=1",
        f"-v={os.getcwd()}:/workspace",
        "-v=/var/run/docker.sock:/var/run/docker.sock:ro",
        "--entrypoint=/bin/bash",
        CONTAINER_IMAGE,
        "-c",
        f"{render_cmd} && {chmod_cmd}",
    ]

    logger.debug(f"Rendering: {shlex.join(docker_cmd)}")
    result = subprocess.run(docker_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Rendering {app.name} with {values_file} failed:\n{result.stderr}")

    return read_yaml(compose_path)


def parse_user(service: str, user) -> tuple[int, int]:
    """Parse a compose "uid:gid" user directive."""
    uid, _, gid = user.partition(":") if isinstance(user, str) else ("", "", "")
    if not uid.isdigit() or not gid.isdigit():
        raise ValueError(f"Service {service} has invalid user directive: {user!r}. Expected numeric 'uid:gid'")
    return int(uid), int(gid)


def analyze(app: App) -> Analysis:
    analysis = Analysis(service_names=set(), capabilities=defaultdict(set), users=defaultdict(list))

    for values_file in app.test_values:
        logger.debug(f"Processing {app.name} with {values_file}")
        services = render(app, values_file).get("services")
        if not services:
            raise ValueError(f"No services found when rendering {app.name} with {values_file}")

        for name, config in services.items():
            restart = config.get("restart", "")
            # Short-lived services (init/setup containers) are not part of the app's surface
            if restart.startswith("on-failure"):
                logger.debug(f"Skipping short-lived service: {name}")
                continue
            analysis.service_names.add(name)

            if not restart:
                logger.warning(f"No restart policy for service: {name}")
                continue

            if "cap_drop" not in config:
                logger.error(
                    f"No cap_drop for service: {name}. Consider explicitly setting the defaults via cap_add "
                    "https://github.com/moby/moby/blob/7a0bf747f5c25da0794e42d5f9e5a40db5a7786e/oci/caps/defaults.go#L4"
                )
            elif config["cap_drop"] != ["ALL"]:
                logger.error(f"Non-standard cap_drop for service: {name}")

            for capability in config.get("cap_add") or []:
                analysis.capabilities[capability].add(name)

            analysis.users[name].append(parse_user(name, config.get("user", "0:0")))

    return analysis


# Metadata generation


def normalize_name(name: str) -> str:
    return name.lower().replace("_", "").replace("-", "").replace(" ", "")


def service_title(service: str, app_title: str) -> str:
    if normalize_name(service) == normalize_name(app_title):
        return app_title
    if service.lower() in SERVICE_TITLES:
        return SERVICE_TITLES[service.lower()]
    return service.replace("-", " ").replace("_", " ").title()


def describe_capability(capability: str, services: set[str], app_title: str) -> str:
    # Numbered replicas (e.g. worker-1, worker-2) are described once
    base_names = {re.sub(r"-\d+$", "", service) for service in services}
    titles = sorted(service_title(name, app_title) for name in base_names)

    description = CAPABILITY_DESCRIPTIONS[capability]
    if len(titles) == 1:
        return f"{titles[0]} is {description}"
    return f"{', '.join(titles)} are {description}"


def build_capabilities(capabilities: dict[str, set[str]], app_title: str) -> list[dict]:
    entries = []
    for capability, services in capabilities.items():
        if capability not in CAPABILITY_DESCRIPTIONS:
            logger.error(f"Unknown capability: {capability}")
            continue
        entries.append({"description": describe_capability(capability, services, app_title), "name": capability})
    return sorted(entries, key=lambda c: c["name"])


def select_service_user(service: str, user_values: list[tuple[int, int]]) -> tuple[int, int]:
    """Pick the user to report for a service from the values of all test configurations."""
    # If all test values have the same user, use that
    if len(set(user_values)) == 1:
        return user_values[0]

    # 568 only differs across test values when it comes from a user-configurable
    # run_as, so the service can run as any user (root included, if the user picks it)
    if (APPS_ID, APPS_ID) in user_values:
        return (APPS_ID, APPS_ID)

    # If at least one test value runs as root, the service runs as root.
    # Prefer entry with both uid=0 and gid=0, then uid=0, then gid=0
    for matches in (
        lambda uid, gid: uid == 0 and gid == 0,
        lambda uid, gid: uid == 0,
        lambda uid, gid: gid == 0,
    ):
        for uid, gid in user_values:
            if matches(uid, gid):
                return (uid, gid)

    # If test values have different non-root users, use the most common one
    # (lowest uid/gid on ties). This shouldn't normally happen, but we handle it
    selected = min(set(user_values), key=lambda value: (-user_values.count(value), value))
    logger.warning(f"Service {service} has inconsistent user values: {user_values}, using {selected}")
    return selected


def host_name(kind: str, names: dict[int, str], id_: int) -> str:
    if id_ not in names:
        logger.warning(f"Unknown host {kind} id: {id_}")
        return f"Host {kind} is [unknown ({id_})]"
    return f"Host {kind} is [{names[id_]}]"


def describe_user(service: str, uid: int, gid: int) -> str:
    kinds = {0: "root", APPS_ID: "any non-root"}
    user, group = kinds.get(uid, "non-root"), kinds.get(gid, "non-root")
    verb = "can run" if uid == APPS_ID else "runs"
    # "user and group" when both are the same kind, e.g. "root user and group"
    if user == group:
        return f"Container [{service}] {verb} as {user} user and group."
    return f"Container [{service}] {verb} as {user} user and {group} group."


def build_run_as_context(users: dict[str, tuple[int, int]]) -> list[dict]:
    return [
        {
            "description": describe_user(service, uid, gid),
            "gid": gid,
            "group_name": host_name("group", GROUP_NAMES, gid),
            "uid": uid,
            "user_name": host_name("user", USER_NAMES, uid),
        }
        for service, (uid, gid) in sorted(users.items())
    ]


def is_ix_app(app: App) -> bool:
    return app.train == "stable" and app.name == "ix-app"


def get_app_version(app: App, app_config: dict) -> str:
    # ix-app has no image of its own, its version is the app_version
    if is_ix_app(app):
        return app_config["version"]

    values_path = app.path / APP_VALUES_FILE
    # "images.image" is the main image of the app, its tag is used as the app_version
    image = (read_yaml(values_path).get("images") or {}).get("image")
    if not isinstance(image, dict):
        raise ValueError(f"Missing [images.image] in {values_path}, it is required for the app_version")
    tag = image.get("tag")
    if not tag or not isinstance(tag, str):
        raise ValueError(f"Missing or non-string [images.image.tag] in {values_path}")
    # Drop the digest pin (tag@sha256:...), it is not part of the version
    return tag.split("@")[0]


def bump_patch_version(version: str) -> str:
    parts = version.split(".")
    if len(parts) != 3 or not parts[2].isdigit():
        raise ValueError(f"Invalid version format: {version}, must be x.y.z")
    parts[2] = str(int(parts[2]) + 1)
    return ".".join(parts)


def get_git_date_added(app: App) -> str:
    """Date of the commit that added the app's app.yaml (the latest one, if it was ever re-added)."""
    path = app.path / APP_METADATA_FILE
    result = subprocess.run(
        ["git", "log", "--diff-filter=A", "--format=%as", "--", str(path)], capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to get git log for {path}:\n{result.stderr}")
    dates = result.stdout.split()
    if not dates:
        raise ValueError(f"{path} has not been committed, can't get date_added from git")
    # git log lists newest first
    return dates[0]


# Validation


def find_question(questions: list[dict], variable: str) -> dict | None:
    return next((q for q in questions if q.get("variable") == variable), None)


def validate_question(question: dict) -> None:
    if "variable" not in question:
        raise ValueError(f"Question missing variable field: {question}")

    variable = question["variable"]
    if variable not in VAR_NAME_EXCEPTIONS and not RE_VAR_NAME.match(variable):
        raise ValueError(f"Invalid variable name: {variable}")

    schema = question["schema"]
    if schema["type"] == "dict":
        for attr in schema["attrs"]:
            validate_question(attr)
    elif schema["type"] == "list":
        if "min_length" in schema:
            raise ValueError(f"List schema with min_length not supported, use min: {schema}")
        for item in schema["items"]:
            validate_question(item)


def check_containers_enum(question: dict, section: str, service_names: set[str]) -> None:
    current = {item["value"] for item in question["schema"]["enum"]}
    if current != service_names:
        raise ValueError(f"Container {section} section should have {sorted(service_names)} but has {sorted(current)}")


def validate_questions(app: App, service_names: set[str]) -> None:
    questions = read_yaml(app.path / QUESTIONS_FILE).get("questions", [])
    for question in questions:
        validate_question(question)

    # The containers enums must list exactly the app's services
    # questions.labels[].containers[]
    if labels := find_question(questions, "labels"):
        label_attrs = labels["schema"]["items"][0]["schema"]["attrs"]
        if containers := find_question(label_attrs, "containers"):
            check_containers_enum(containers["schema"]["items"][0], "labels", service_names)

    # questions.network.networks[].containers[].name
    if network := find_question(questions, "network"):
        if networks := find_question(network["schema"]["attrs"], "networks"):
            network_attrs = networks["schema"]["items"][0]["schema"]["attrs"]
            if containers := find_question(network_attrs, "containers"):
                container_attrs = containers["schema"]["items"][0]["schema"]["attrs"]
                if name := find_question(container_attrs, "name"):
                    check_containers_enum(name, "network.networks.containers.name", service_names)


def validate_images(app: App) -> None:
    """Fail on digest pinned images from registries that prune untagged manifests."""
    values_path = app.path / APP_VALUES_FILE
    if not values_path.exists():
        return

    for name, image in (read_yaml(values_path).get("images") or {}).items():
        repo = image.get("repository", "")
        tag = str(image.get("tag", ""))
        if repo.startswith(NO_DIGEST_PIN_REGISTRIES) and "@" in tag:
            raise ValueError(
                f"Image [{name}] ({repo}) must not be pinned to a digest in {values_path}. "
                f"Registries {list(NO_DIGEST_PIN_REGISTRIES)} prune manifests that are no longer tagged."
            )


def validate_app_config(app: App, app_config: dict) -> None:
    categories = app_config.get("categories", [])
    if len(categories) > 1:
        raise ValueError(f"app.yaml must have exactly 1 category, found {len(categories)}: {categories}")

    for field in ("date_added", "changelog_url"):
        if field not in app_config:
            logger.warning(f"{app.name}: missing {field}")

    app_media_url = f"{MEDIA_BASE_URL}/{app_config.get('name', app.name)}"
    media = [("icon", app_config.get("icon", ""), "icons")]
    media += [("screenshot", url, "screenshots") for url in app_config.get("screenshots", [])]
    for kind, url, subdir in media:
        if not url.startswith(MEDIA_BASE_URL):
            raise ValueError(f"Invalid {kind} URL: {url}. Must use {MEDIA_BASE_URL} as base")
        if not url.startswith(f"{app_media_url}/{subdir}/"):
            logger.warning(f"{app.name}: invalid {kind} URL: {url}")


# Main flow


def update_app(app: App, bump_version: bool, set_date_added: bool) -> None:
    if not app.test_values:
        raise ValueError(f"No test values found in {app.path / TEST_VALUES_DIR}")

    app_config_path = app.path / APP_METADATA_FILE
    app_config = read_yaml(app_config_path)
    app_title = app_config.get("title", app.name)

    analysis = analyze(app)
    validate_questions(app, analysis.service_names)
    validate_images(app)
    validate_app_config(app, app_config)

    users = {service: select_service_user(service, values) for service, values in analysis.users.items()}
    capabilities = build_capabilities(analysis.capabilities, app_title)
    app_version = get_app_version(app, app_config)

    old_app_version = app_config.get("app_version")
    # Keep a shorter app_version that the tag extends, e.g. tag 1.2.3-debian and app_version 1.2.3
    if old_app_version and old_app_version in app_version:
        app_version = old_app_version
    run_as_context = build_run_as_context(users)

    changed = (
        # ix-app's app_version just follows its version, so it never needs a bump of its own
        (old_app_version != app_version and not is_ix_app(app))
        or sorted(app_config.get("capabilities") or [], key=lambda c: c["name"]) != capabilities
        or (app_config.get("run_as_context") or []) != run_as_context
    )
    app_config.update(app_version=app_version, capabilities=capabilities, run_as_context=run_as_context)

    if app_config.get("maintainers", []) != MAINTAINERS:
        app_config["maintainers"] = MAINTAINERS
        changed = True

    sources = set(app_config.get("sources", []))
    app_source = f"https://apps.truenas.com/catalog/{app.name}_{app.train}/"
    if app_source not in sources:
        app_config["sources"] = sorted(sources | {app_source})
        changed = True

    if set_date_added:
        date_added = get_git_date_added(app)
        # str() as an unquoted date in the yaml loads as a date object
        if str(app_config.get("date_added")) != date_added:
            logger.info(f"Updated {app.name} date_added: {app_config.get('date_added')} → {date_added}")
            app_config["date_added"] = date_added
            changed = True

    if changed and bump_version:
        old_version = app_config["version"]
        app_config["version"] = bump_patch_version(old_version)
        logger.info(f"Updated {app.name} version: {old_version} → {app_config['version']}")
        if is_ix_app(app):
            app_config["app_version"] = app_config["version"]

    write_yaml(app_config_path, app_config)
    logger.info(f"Successfully updated {app.name} with {len(capabilities)} capabilities and {len(users)} services")


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze rendered TrueNAS apps and update their app.yaml metadata")
    parser.add_argument("--train", help="Specific train name to process")
    parser.add_argument("--app", help="Specific app name to process (requires --train)")
    parser.add_argument("--no-bump", action="store_true", help="Skip version bumping when updating metadata")
    parser.add_argument(
        "--set-date-added",
        action="store_true",
        help="Set date_added from the commit that added app.yaml. "
        "Needs app.yaml to be committed and the full git history (not a shallow clone)",
    )
    args = parser.parse_args()

    if bool(args.train) != bool(args.app):
        parser.error("Both --train and --app must be provided together, or neither")

    if args.set_date_added:
        shallow = subprocess.run(["git", "rev-parse", "--is-shallow-repository"], capture_output=True, text=True)
        if shallow.returncode != 0 or shallow.stdout.strip() != "false":
            parser.error("--set-date-added needs a git repository with full history (not a shallow clone)")

    if args.train:
        app = load_app(args.train, APPS_ROOT_DIR / args.train / args.app)
        if not app:
            logger.error(f"App {args.train}/{args.app} not found")
            sys.exit(1)
        apps = [app]
    else:
        apps = load_all_apps()

    failed = []
    for app in apps:
        try:
            update_app(app, bump_version=not args.no_bump, set_date_added=args.set_date_added)
        except Exception as e:
            logger.error(f"Failed to update {app.train}/{app.name}: {e}")
            failed.append(app)

    if len(apps) > 1:
        logger.info(f"Successfully processed {len(apps) - len(failed)}/{len(apps)} apps")
    if failed:
        logger.error(f"Failed to process {len(failed)} apps: {', '.join(f'{a.train}/{a.name}' for a in failed)}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
