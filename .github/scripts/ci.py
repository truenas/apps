#!/usr/bin/env python3

# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pyyaml",
# ]
# ///

import subprocess
import argparse
import platform
import secrets
import shutil
import shlex
import copy
import json
import yaml
import sys

import generate_metadata
from common import (
    APPS_ROOT_DIR,
    CONTAINER_IMAGE,
    PLATFORM,
    RENDERED_COMPOSE_PATH,
    TEST_VALUES_DIR,
    YAML_LOADER,
    hash_generate_cmd,
    render_app_cmd,
)

CHANGE_PLATFORM_FOR_IMAGES = [
    "redis",
    "valkey/valkey",
    "chaptarr/chaptarr",
    "ghcr.io/lostb1t/remux",
    "ghcr.io/stalwartlabs/stalwart",
    "ghcr.io/euro-office/documentserver",
    "ghcr.io/karakeep-app/karakeep-chrome",
]


# Used to print mostly structured data, like yaml or json
# so they can be piped to a file or jq, etc
def print_stdout(msg):
    print(msg)


# Prints to stderr so the output is not mixed with stdout
def print_stderr(msg):
    print(msg, file=sys.stderr)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--app",
        required=True,
        help="The name of the app",
    )
    parser.add_argument(
        "--train",
        required=True,
        help="The name of the train for the app",
    )
    parser.add_argument(
        "--test-file",
        required=True,
        help="Name of the test file to use as values",
    )
    parser.add_argument(
        "--render-only",
        required=False,
        default=False,
        type=bool,
        help="Prints the rendered docker-compose file",
    )
    parser.add_argument(
        "--render-only-debug",
        required=False,
        default=False,
        type=bool,
        help="Prints the rendered docker-compose file even if it's not a valid yaml",
    )
    parser.add_argument(
        "--wait",
        required=False,
        default=False,
        type=bool,
        help="Wait for user input before stopping the app",
    )
    parser.add_argument(
        "--skip-metadata",
        action="store_true",
        help="Don't update the app metadata (app.yaml, item.yaml) before rendering",
    )
    parsed = parser.parse_args()

    return {
        "app": parsed.app,
        "train": parsed.train,
        "test_file": parsed.test_file,
        "render_only": parsed.render_only,
        "render_only_debug": parsed.render_only_debug,
        "project": secrets.token_hex(16),
        "wait": parsed.wait,
        "skip_metadata": parsed.skip_metadata,
    }


def print_info():
    print_stderr("Parameters:")
    print_stderr(f"  - app: [{args['app']}]")
    print_stderr(f"  - train: [{args['train']}]")
    print_stderr(f"  - project: [{args['project']}]")
    print_stderr(f"  - test-file: [{args['test_file']}]")
    print_stderr(f"  - render-only: [{args['render_only']}]")
    print_stderr(f"  - render-only-debug: [{args['render_only_debug']}]")
    print_stderr(f"  - wait: [{args['wait']}]")
    print_stderr(f"  - skip-metadata: [{args['skip_metadata']}]")


def command_exists(command):
    return shutil.which(command) is not None


def replace_platform_in_service(svc):
    if sys.platform != "darwin" or platform.machine() != "arm64":
        return svc

    svc_copy = copy.deepcopy(svc)
    image = svc.get("image", "")
    if not image:
        print_stderr("No image found in service definition. Skipping platform replacement.")
        sys.exit(1)
    repo = image.split(":")[0]
    if repo in CHANGE_PLATFORM_FOR_IMAGES:
        svc_copy["platform"] = "linux/arm64"
        # Drop the digest pin (repo:tag@sha256:...), it might not include an arm64 image
        svc_copy["image"] = image.split("@")[0]
    return svc_copy


def check_required_commands():
    required_commands = ["docker", "jq", "openssl"]
    for command in required_commands:
        if not command_exists(command):
            print_stderr(f"Error: command [{command}] is not installed")
            sys.exit(1)


def get_app_dir():
    return APPS_ROOT_DIR / args["train"] / args["app"]


def get_base_cmd():
    return f"docker compose -p {args['project']} -f {get_app_dir() / RENDERED_COMPOSE_PATH}"


def pull_app_catalog_container():
    print_stderr(f"Pulling container image [{CONTAINER_IMAGE}]")
    res = subprocess.run(
        f"docker pull --platform {PLATFORM} --quiet {CONTAINER_IMAGE}",
        shell=True,
        capture_output=True,
    )
    if res.returncode != 0:
        print_stderr(f"Failed to pull container image [{CONTAINER_IMAGE}]")
        sys.exit(1)
    print_stderr(f"Done pulling container image [{CONTAINER_IMAGE}]")


def render_compose():
    print_stderr("Rendering docker-compose file")
    app_dir = get_app_dir()
    cmd = render_app_cmd(app_dir, app_dir / TEST_VALUES_DIR / args["test_file"])
    print_cmd(shlex.join(cmd))
    separator_start()
    res = subprocess.run(cmd)
    separator_end()
    if res.returncode != 0:
        print_stderr("Failed to render docker-compose file")
        sys.exit(1)

    template_file = app_dir / RENDERED_COMPOSE_PATH

    with open(template_file, "r") as f:
        try:
            out = yaml.load(f, Loader=YAML_LOADER)
            # Replace platform on some known images that refuse to work on
            # arm64 when platform is set to linux/amd64.
            for svc_name, svc in out.get("services", {}).items():
                new_svc = replace_platform_in_service(svc)
                out["services"][svc_name] = new_svc
            with open(template_file, "w") as f2:
                yaml.dump(out, f2)

        except yaml.YAMLError as e:
            print_stderr(f"Failed to parse rendered docker-compose file [{e}]")
            with open(template_file, "r") as f:
                print_stderr(f"Syntax Error in rendered docker-compose file:\n{f.read()}")
            sys.exit(1)

        if args["render_only_debug"]:
            print_stderr("Successfully rendered docker-compose file:")
            print_stdout(yaml.dump(out))
            sys.exit(0)

    print_stderr("Done rendering docker-compose file")


def update_x_portals(parsed_compose):
    portals = parsed_compose.get("x-portals", [])
    for portal in portals:
        scheme = portal.get("scheme", "http")
        host = portal.get("host", "localhost").replace("0.0.0.0", "localhost")
        port = str(portal.get("port", "80" if scheme == "http" else "443"))
        url = scheme + "://" + host + ":" + port + portal.get("path", "")
        x_portals.append(f"[{portal['name']}] - {url}")


def print_docker_compose_config():
    print_stderr("Printing docker compose config (parsed compose)")
    cmd = f"{get_base_cmd()} config"
    print_cmd(cmd)
    separator_start()
    res = subprocess.run(cmd, shell=True, capture_output=True)
    separator_end()
    if res.returncode != 0:
        print_stderr("Failed to print docker compose config")
        if res.stdout:
            print_stderr(res.stdout.decode("utf-8"))
        if res.stderr:
            print_stderr(res.stderr.decode("utf-8"))
        sys.exit(1)

    if args["render_only"]:
        print_stdout(res.stdout.decode("utf-8"))
        sys.exit(0)

    data = yaml.load(res.stdout.decode("utf-8"), Loader=YAML_LOADER)
    update_x_portals(data)

    print_stderr(res.stdout.decode("utf-8"))


def separator_start():
    print_stderr("=" * 40 + "+++++" + "=" * 40)


def separator_end():
    print_stderr("=" * 40 + "-----" + "=" * 40)


def print_cmd(cmd):
    print_stderr(f"Running command [{cmd}]")


def docker_cleanup():
    cmd = f"{get_base_cmd()} down --remove-orphans --volumes"
    print_cmd(cmd)
    separator_start()
    subprocess.run(cmd, shell=True)
    separator_end()

    cmd = f"{get_base_cmd()} rm --force --stop --volumes"
    print_cmd(cmd)
    separator_start()
    subprocess.run(cmd, shell=True)
    separator_end()


def print_logs():
    # Get all service names
    ps = f"{get_base_cmd()} ps --all --format" + " {{.Service}}"
    print_cmd(ps)
    res = subprocess.run(ps, shell=True, capture_output=True)
    if res.returncode != 0:
        print_stderr("Failed to get running containers")
        sys.exit(1)

    # Parse output
    services = res.stdout.decode("utf-8").split("\n")
    if not services:
        print_stderr("No services found to print logs for")
        return

    # Remove empty lines and whitespace
    services = [s.strip() for s in services if s.strip()]
    for service in services:
        cmd = f"{get_base_cmd()} logs {service}"
        print_cmd(cmd)
        separator_start()
        subprocess.run(cmd, shell=True)
        separator_end()


def print_docker_processes():
    cmd = f"{get_base_cmd()} ps --all"
    print_cmd(cmd)
    separator_start()
    subprocess.run(cmd, shell=True)
    separator_end()


def get_parsed_containers():
    # Outputs one container per line, in json format
    cmd = f"{get_base_cmd()} ps --all --format json"
    print_cmd(cmd)
    all_containers = subprocess.run(cmd, shell=True, capture_output=True).stdout.decode("utf-8")
    parsed_containers = []
    for line in all_containers.split("\n"):
        if not line:
            continue
        try:
            parsed_containers.append(json.loads(line))
        except json.JSONDecodeError:
            print_stderr(f"Failed to parse container status output:\n {line}")
            sys.exit(1)
    return parsed_containers


def status_indicates_healthcheck_existence(container):
    """Assumes healthcheck exists if status contains "health" """
    # eg "health: starting". This happens right after a container is started or restarted
    return "(health: starting)" in container.get("Status", "")


def state_indicates_restarting(container):
    """Assumes restarting if state is "restarting" """
    return container.get("State", "") == "restarting"


def exit_code_indicates_normal_exit(container):
    """Assumes normal exit if there is no exit code or if it is 0"""
    return container.get("ExitCode", 0) == 0


def health_indicates_healthy(container):
    """Assumes healthy if there is no health status or if it is "healthy" """
    health = container.get("Health", "")
    if health in ["healthy", ""]:
        return True
    return False


def is_considered_healthy(container):
    message = [
        f"✅ Healthy container skipped [{container['Name']}({container['ID']})] with status [{container.get('State')}]"
        + " for the following reasons:"
    ]
    reasons = []

    if health_indicates_healthy(container):
        reasons.append("\t- Container is healthy")

    if exit_code_indicates_normal_exit(container):
        reasons.append(f"\t- Exit code is [{container.get('ExitCode', 0)}]")

    if not state_indicates_restarting(container):
        reasons.append("\t- Container is not restarting")

    if not status_indicates_healthcheck_existence(container):
        reasons.append("\t- Status does not indicate a healthcheck exists")

    # Mark it as healthy if ALL of the following are true:
    # 1. It is healthy
    # 2. Its exit code is normal
    # 3. Its not restarting
    # 4. It does not indicate a healthcheck exists

    # For #4, there was some cases where the container was restarting and at the time of check,
    # the "Health" was empty and "State" was "running" (similar to init containers). This check
    # added to try to catch those cases, by inspecting the "Status" field which if there is a healthcheck
    # it will contain the word "health".
    result = (
        health_indicates_healthy(container)
        and exit_code_indicates_normal_exit(container)
        and not state_indicates_restarting(container)
        and not status_indicates_healthcheck_existence(container)
    )

    return {"result": result, "reasons": "\n".join(message + reasons)}


def get_failed_containers():
    parsed_containers = get_parsed_containers()

    failed = []
    for container in parsed_containers:
        # Skip containers that are exited with 0 (eg init containers),
        # but not restarting (during a restart exit code is 0)
        is_healthy = is_considered_healthy(container)
        if is_healthy["result"]:
            print_stderr(is_healthy["reasons"])
            continue
        failed.append(container)

    return failed


def get_container_name(container):
    return container["Name"].replace(args["project"] + "-", "")


def print_inspect_data(container):
    cmd = f"docker container inspect {container['ID']}"
    print_cmd(cmd + f". Container: [{get_container_name(container)}]]")
    res = subprocess.run(cmd, shell=True, capture_output=True)
    data = json.loads(res.stdout.decode("utf-8"))
    separator_start()
    print_stdout(json.dumps(data, indent=4))
    separator_end()


def run_app():
    cmd = f"{get_base_cmd()} up --detach --quiet-pull --wait --wait-timeout 600"
    print_cmd(cmd)
    res = subprocess.run(cmd, shell=True, capture_output=True)

    print_docker_processes()
    print_logs()

    print_stderr(f"Exit code: {res.returncode}")
    if res.returncode != 0:
        stderr = res.stderr.decode("utf-8")
        err_msg = "error response from daemon"
        if err_msg in stderr.lower():
            print_stderr(
                "\nDocker exited with non-zero code and no containers were found.\n"
                + "Most likely docker couldn't start one of the containers at all.\n"
                + "Such cases are for example when a device is not available on the host.\n"
                + "or image cannot be found.\n\n"
                + stderr
            )
            return res.returncode or 99
        parsed_containers = get_parsed_containers()
        if not parsed_containers:
            print_stderr(
                "Docker exited with non-zero code and no containers were found.\n"
                + "Most likely docker couldn't start the containers at all.\n\n"
                + stderr
            )
            return res.returncode or 99

        failed_containers = get_failed_containers()
        failed_containers_names = "\n".join([f"\t-{c['Name']} ({c['ID']})" for c in failed_containers])
        if not failed_containers:
            print_stderr("✅ No failed containers found")

        else:
            print_stderr(
                f"❌ Found [{len(failed_containers)}]"
                + f"failed containers that failed to start:\n {failed_containers_names}"
            )
        for container in failed_containers:
            print_stderr(f"Container [{container['Name']}({container['ID']})] exited. Printing Inspect Data")
            print_inspect_data(container)

        # https://github.com/docker/compose/issues/10596
        # `--wait` will return 1 even if a container exits with 0.
        # Although it seems that it only happens on specific compose files, while on others it is not.

        # Cases that a container exits with 0 that are expected is for example an init container.
        return res.returncode if len(failed_containers) > 0 else 0

    print_stderr("Containers started successfully")
    return 0


def check_app_dir_exists():
    if not get_app_dir().is_dir():
        print_stderr(f"App directory [{get_app_dir()}] does not exist")
        sys.exit(1)


def copy_lib():
    cmd = hash_generate_cmd([f"--train={args['train']}", f"--app={args['app']}"])
    print_cmd(shlex.join(cmd))
    separator_start()
    res = subprocess.run(cmd, capture_output=True)
    print_stderr(res.stdout.decode("utf-8"))
    separator_end()
    if res.returncode != 0:
        print_stderr("Failed to generate hashes and copy lib")
        print_stderr(res.stderr.decode("utf-8"))
        sys.exit(1)


def update_metadata():
    # Debug renders are for templates that don't render cleanly, metadata would fail on them first
    if args["skip_metadata"] or args["render_only_debug"]:
        print_stderr("Skipping metadata update")
        return

    app = generate_metadata.load_app(args["train"], get_app_dir())
    if not app:
        print_stderr("App has no metadata to update. Skipping metadata update")
        return

    # Renders every test file into the rendered compose, so it has to run before this test's render
    print_stderr("Updating app metadata")
    separator_start()
    try:
        generate_metadata.update_app(app, bump_version=True, set_date_added=False)
    except Exception as e:
        print_stderr(f"Failed to update app metadata: {e}")
        sys.exit(1)
    finally:
        separator_end()


def wait_for_user_input():
    print_stderr("Press enter to stop the app")
    try:
        input()
    except KeyboardInterrupt:
        pass


def main():
    print_info()
    check_app_dir_exists()
    pull_app_catalog_container()
    copy_lib()
    update_metadata()
    check_required_commands()
    render_compose()
    print_docker_compose_config()
    res = run_app()
    if args["wait"]:
        if not x_portals:
            print_stderr("No portals found")
        else:
            print_stderr("\nPortals:")
            print_stderr("\n".join(x_portals) + "\n")
        wait_for_user_input()
    docker_cleanup()

    if res == 0:
        print_stderr("Successfully rendered and run docker-compose file")
    else:
        print_stderr("Failed to render and run docker-compose file")

    sys.exit(res)


args = parse_args()
x_portals = []

if __name__ == "__main__":
    main()
