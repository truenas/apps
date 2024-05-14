#!/usr/bin/env python3
import subprocess
import argparse
import secrets
import shutil
import json
import re
import os

CONTAINER_IMAGE = "sonicaj/a_v:latest"
# CONTAINER_IMAGE = "ghcr.io/truenas/apps_validation:latest"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", required=True, help="App name")
    parser.add_argument("--train", required=True, help="Train name")
    parser.add_argument("--test_file", required=True, help="Test file")
    parsed = parser.parse_args()

    return {
        "app": parsed.app,
        "train": parsed.train,
        "test_file": parsed.test_file,
        "project": secrets.token_hex(16),
    }


def print_state():
    print("Parameters:")
    print(f"  - app: [{args['app']}]")
    print(f"  - train: [{args['train']}]")
    print(f"  - test_file: [{args['test_file']}]")
    print(f"  - project: [{args['project']}]")


def command_exists(command):
    return shutil.which(command) is not None


def check_required_commands():
    required_commands = ["docker", "jq", "openssl"]
    for command in required_commands:
        if not command_exists(command):
            print(f"Error: command [{command}] is not installed")
            exit(1)


def get_base_cmd():
    rendered_compose = "templates/rendered/docker-compose.yaml"
    return " ".join(
        [
            f"docker compose -p {args['project']} -f",
            f"ix-dev/{args['train']}/{args['app']}/{rendered_compose}",
        ]
    )


def pull_app_catalog_container():
    print(f"Pulling container image [{CONTAINER_IMAGE}]")
    res = subprocess.run(f"docker pull --quiet {CONTAINER_IMAGE}", shell=True)
    if res.returncode != 0:
        print(f"Failed to pull container image [{CONTAINER_IMAGE}]")
        exit(1)
    print(f"Done pulling container image [{CONTAINER_IMAGE}]")


def render_compose():
    print("Rendering docker-compose file")
    test_values_dir = "templates/test_values"
    app_dir = f"ix-dev/{args['train']}/{args['app']}"
    cmd = " ".join(
        [
            f"docker run --quiet --rm -v {os.getcwd()}:/workspace {CONTAINER_IMAGE}",
            "python3 /app/catalog_templating/scripts/render_compose.py render",
            f"--path /workspace/{app_dir}",
            f"--values /workspace/{app_dir}/{test_values_dir}/{args['test_file']}",
        ]
    )
    print_cmd(cmd)
    separator_start()
    res = subprocess.run(cmd, shell=True)
    separator_start()
    if res.returncode != 0:
        print("Failed to render docker-compose file")
        exit(1)
    print("Done rendering docker-compose file")


def print_docker_compose_config():
    print("Printing docker compose config (parsed compose)")
    cmd = f"{get_base_cmd()} config"
    print_cmd(cmd)
    separator_start()
    res = subprocess.run(cmd, shell=True)
    separator_start()
    if res.returncode != 0:
        print("Failed to print docker compose config")
        exit(1)


def separator_start():
    print("=" * 40 + "+++++" + "=" * 40)


def separator_end():
    print("=" * 40 + "-----" + "=" * 40)


def print_cmd(cmd):
    print(f"Running command [{cmd}]")


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


def get_failed_containers():
    cmd = f"{get_base_cmd()} ps --status exited --all --format json"
    print_cmd(cmd)
    failed = subprocess.run(cmd, shell=True, capture_output=True)
    failed = failed.stdout.decode("utf-8")
    # if failed starts with { put it inside []
    if failed.startswith("{"):
        failed = f"[{failed}]"

    return json.loads(failed)


def print_inspect_data(container):
    cmd = f"docker container inspect {container['ID']}"
    print_cmd(cmd)
    res = subprocess.run(cmd, shell=True, capture_output=True)
    data = json.loads(res.stdout.decode("utf-8"))
    separator_start()
    print(json.dumps(data, indent=4))
    separator_end()


def run_app():
    cmd = f"{get_base_cmd()} up --detach --quiet-pull --wait --wait-timeout 600"
    print_cmd(cmd)
    res = subprocess.run(cmd, shell=True)

    print_logs()
    print_docker_processes()

    if res.returncode != 0:
        print("Failed to start container(s)")
        for container in get_failed_containers():
            print(f"Container [{container['ID']}] exited. Printing Inspect Data")
            print_inspect_data(container)
        return res.returncode

    print("Containers started successfully")


def check_app_dir_exists():
    if not os.path.exists(f"ix-dev/{args['train']}/{args['app']}"):
        print(f"App directory [ix-dev/{args['train']}/{args['app']}] does not exist")
        exit(1)


def get_latest_lib_version():
    libs = [
        lib
        for lib in os.listdir("library")
        if os.path.isdir(os.path.join("library", lib))
    ]

    def version_key(version):
        return [int(part) for part in re.split(r"\.", version)]

    sorted_libs = sorted(libs, key=version_key)
    return sorted_libs[-1] if sorted_libs else None


def copy_lib():
    # get latest lib version
    lib_version = get_latest_lib_version()
    if not lib_version:
        print("Failed to get latest lib version")
        exit(1)
    print(f"Copying lib version [{lib_version}]")
    lib = f"base_v{lib_version.replace('.', '_')}"
    if os.path.exists(f"ix-dev/{args['train']}/{args['app']}/templates/library/{lib}"):
        shutil.rmtree(f"ix-dev/{args['train']}/{args['app']}/templates/library/{lib}")
    os.makedirs(
        f"ix-dev/{args['train']}/{args['app']}/templates/library/{lib}", exist_ok=True
    )
    try:
        shutil.copytree(
            f"library/{lib_version}",
            f"ix-dev/{args['train']}/{args['app']}/templates/library/{lib}",
            dirs_exist_ok=True,
        )
    except shutil.Error:
        print(f"Failed to copy lib [{lib_version}]")
        exit(1)


def main():
    print_state()
    check_app_dir_exists()
    copy_lib()
    check_required_commands()
    pull_app_catalog_container()
    render_compose()
    print_docker_compose_config()
    res = run_app()
    docker_cleanup()

    exit(res)


args = parse_args()

if __name__ == "__main__":
    main()
