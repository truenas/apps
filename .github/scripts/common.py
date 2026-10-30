"""Shared constants and helpers of the .github/scripts tools."""

import os
import shlex
from pathlib import Path

import yaml

CONTAINER_IMAGE = "ghcr.io/truenas/apps_validation:slim"
PLATFORM = "linux/amd64"

APPS_ROOT_DIR = Path("ix-dev")
LIBRARY_DIR = Path("library")
# Unversioned source of an app's own library, copied to templates/library/<train>/<app>/v<version>
APP_LIBRARY_SOURCE_DIR = "lib"
TEST_VALUES_DIR = "templates/test_values"
RENDERED_COMPOSE_PATH = "templates/rendered/docker-compose.yaml"
APP_METADATA_FILE = "app.yaml"
QUESTIONS_FILE = "questions.yaml"

# libyaml-backed loader is much faster; fall back if PyYAML was built without it
YAML_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


def read_yaml(path: Path) -> dict:
    with open(path) as f:
        data = yaml.load(f, Loader=YAML_LOADER)
    if not isinstance(data, dict):
        raise ValueError(f"YAML file {path} must contain a dictionary at root level, got {type(data)}")
    return data


def write_yaml(path: Path, data: dict) -> None:
    with open(path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def catalog_container_cmd(options: list[str], command: list[str]) -> list[str]:
    """docker run command for the apps_validation container, with the repo mounted at /workspace."""
    return [
        "docker",
        "run",
        f"--platform={PLATFORM}",
        "--quiet",
        "--rm",
        "-e",
        "FAKE_ENV=1",
        f"-v={os.getcwd()}:/workspace",
        *options,
        CONTAINER_IMAGE,
        *command,
    ]


def render_app_cmd(app_path: Path | str, values_path: Path | str, readme: bool = False) -> list[str]:
    """Render the app into its templates/rendered/docker-compose.yaml.

    With readme, the library also renders the x-readme data the app's README.md is generated from.
    """
    render = shlex.join(
        ["apps_render_app", "render", f"--path=/workspace/{app_path}", f"--values=/workspace/{values_path}"]
    )
    # Drop to the host user so the rendered files are owned by it, keeping the socket's group
    # so the renderer can still reach docker. The group is read inside the container, it is not
    # always the host's (eg Docker Desktop shows the socket as root:root, Linux keeps the docker group)
    drop_privs = (
        f"setpriv --reuid={os.getuid()} --regid={os.getgid()} --groups=$(stat -c %g /var/run/docker.sock) --"
    )
    options = ["-v=/var/run/docker.sock:/var/run/docker.sock:ro", "--entrypoint=/bin/bash"]
    if readme:
        options.append("-e=IX_RENDER_README=1")
    return catalog_container_cmd(options, ["-c", f"{drop_privs} {render}"])


def markdown_to_html_cmd() -> list[str]:
    """Convert the markdown on stdin to HTML, the way apps_validation converts an app's README for the catalog."""
    return catalog_container_cmd(
        ["-i", "--entrypoint=python3"],
        ["-c", "import sys, markdown; sys.stdout.write(markdown.markdown(sys.stdin.read()))"],
    )


def hash_generate_cmd(args: list[str]) -> list[str]:
    """Copy the library into the apps and update their lib_version_hash."""
    return catalog_container_cmd(
        # Keep the copied library and app.yaml files owned by the host user
        [f"--user={os.getuid()}:{os.getgid()}"],
        ["apps_catalog_hash_generate", "--path=/workspace", *args],
    )
