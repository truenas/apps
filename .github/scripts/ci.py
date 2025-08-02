#!/usr/bin/env python3

# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pyyaml",
# ]
# ///

import subprocess
import argparse
import pathlib
import secrets
import shutil
import json
import yaml
import sys
import os

CONTAINER_IMAGE = "ghcr.io/truenas/apps_validation:latest"
PLATFORM = "linux/amd64"


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
    parsed = parser.parse_args()

    return {
        "app": parsed.app,
        "train": parsed.train,
        "test_file": parsed.test_file,
        "render_only": parsed.render_only,
        "render_only_debug": parsed.render_only_debug,
        "project": secrets.token_hex(16),
        "wait": parsed.wait,
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


def command_exists(command):
    return shutil.which(command) is not None


def check_required_commands():
    required_commands = ["docker", "jq", "openssl"]
    for command in required_commands:
        if not command_exists(command):
            print_stderr(f"Error: command [{command}] is not installed")
            sys.exit(1)


def get_base_cmd():
    rendered_compose = "templates/rendered/docker-compose.yaml"
    return " ".join(
        [
            f"docker compose -p {args['project']} -f",
            f"ix-dev/{args['train']}/{args['app']}/{rendered_compose}",
        ]
    )


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


def fix_permissions(file_path):
    print_stderr("Fixing permissions")
    cmd = " ".join(
        [
            f"docker run --platform {PLATFORM} --quiet --rm -v {os.getcwd()}:/workspace",
            f"--entrypoint /bin/bash {CONTAINER_IMAGE} -c 'chmod 777 /workspace/{file_path}'",
        ]
    )
    res = subprocess.run(cmd, shell=True, capture_output=True)
    if res.returncode != 0:
        print_stderr(f"Failed to fix permissions for file [{file_path}]")
        print_stderr(res.stderr.decode("utf-8"))
        sys.exit(1)
    print_stderr(f"Done fixing permissions for file [{file_path}]")


def render_compose():
    print_stderr("Rendering docker-compose file")
    test_values_dir = "templates/test_values"
    app_dir = f"ix-dev/{args['train']}/{args['app']}"
    cmd = " ".join(
        [
            f"docker run --platform {PLATFORM} --quiet --rm -v {os.getcwd()}:/workspace {CONTAINER_IMAGE}",
            "apps_render_app render",
            f"--path /workspace/{app_dir}",
            f"--values /workspace/{app_dir}/{test_values_dir}/{args['test_file']}",
        ]
    )
    print_cmd(cmd)
    separator_start()
    res = subprocess.run(cmd, shell=True)
    separator_start()
    if res.returncode != 0:
        print_stderr("Failed to render docker-compose file")
        sys.exit(1)

    template_file = f"{app_dir}/templates/rendered/docker-compose.yaml"
    fix_permissions(template_file)

    with open(template_file, "r") as f:
        try:
            out = yaml.safe_load(f)
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

    data = yaml.safe_load(res.stdout.decode("utf-8"))
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
    cmd = f"{get_base_cmd()} logs"
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
        if res.stderr:
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
                + "Most likely docker couldn't start the containers at all.\n"
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
    if not os.path.exists(f"ix-dev/{args['train']}/{args['app']}"):
        print_stderr(f"App directory [ix-dev/{args['train']}/{args['app']}] does not exist")
        sys.exit(1)


def copy_lib():
    cmd = " ".join(
        [
            f"docker run --platform {PLATFORM} --quiet --rm -v {os.getcwd()}:/workspace {CONTAINER_IMAGE}",
            "apps_catalog_hash_generate --path /workspace",
        ]
    )
    print_cmd(cmd)
    separator_start()
    res = subprocess.run(cmd, shell=True, capture_output=True)
    print_stderr(res.stdout.decode("utf-8"))
    separator_start()
    if res.returncode != 0:
        print_stderr("Failed to generate hashes and copy lib")
        sys.exit(1)


def copy_macros():
    if not os.path.exists("macros"):
        print_stderr("Macros directory does not exist. Skipping macros copy")
        return

    print_stderr("Copying macros")
    target_macros_dir = f"ix-dev/{args['train']}/{args['app']}/templates/macros/global"
    os.makedirs(target_macros_dir, exist_ok=True)
    if pathlib.Path(target_macros_dir).exists():
        shutil.rmtree(target_macros_dir, ignore_errors=True)

    try:
        shutil.copytree("macros", target_macros_dir, dirs_exist_ok=True)
    except shutil.Error:
        print_stderr("Failed to copy macros")
        sys.exit(1)


def generate_item_file():
    with open(f"ix-dev/{args['train']}/{args['app']}/app.yaml", "r") as f:
        app_yaml = yaml.safe_load(f)

    item_file = f"ix-dev/{args['train']}/{args['app']}/item.yaml"
    item_data = {
        "icon_url": app_yaml.get("icon", ""),
        "categories": app_yaml.get("categories", []),
        "screenshots": app_yaml.get("screenshots", []),
        "tags": app_yaml.get("keywords", []),
    }
    with open(item_file, "w") as f:
        yaml.dump(item_data, f)


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
    copy_macros()
    generate_item_file()
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
