#!/usr/bin/env python3
"""Validate ABDM's TrueNAS catalog metadata and render the Compose template locally."""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import yaml
from jinja2 import Environment

APP_DIR = Path(__file__).resolve().parent
LIB_DIR = APP_DIR / "templates" / "library"


def read_yaml(path: Path):
    with path.open(encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def render_compose(values: dict) -> dict:
    """Render with the app's vendored TrueNAS library (no Docker needed)."""
    sys.path.insert(0, str(LIB_DIR))
    from base_v2_3_17.render import Render  # noqa: PLC0415

    ix_lib = SimpleNamespace(base=SimpleNamespace(render=SimpleNamespace(Render=Render)))
    env = Environment(extensions=["jinja2.ext.do"])
    template = env.from_string((APP_DIR / "templates/docker-compose.yaml").read_text(encoding="utf-8"))
    output = template.render(values=values, ix_lib=ix_lib)
    return json.loads(output)


def assert_catalog_files() -> None:
    app = read_yaml(APP_DIR / "app.yaml")
    questions = read_yaml(APP_DIR / "questions.yaml")
    values = read_yaml(APP_DIR / "ix_values.yaml")
    fixture = read_yaml(APP_DIR / "templates/test_values/basic-values.yaml")
    assert app["annotations"]["min_scale_version"] == "25.10.0"
    assert app["lib_version"] == "2.3.17"
    assert app["name"] == "abdm"
    assert {q["variable"] for q in questions["questions"]} >= {"abdm", "storage", "network"}
    assert set(values["consts"]) >= {"abdm_container_name", "config_path", "downloads_path", "temp_path"}
    assert set(fixture["storage"]) == {"config", "downloads", "temp"}
    storage_question = next(q for q in questions["questions"] if q["variable"] == "storage")
    for storage in storage_question["schema"]["attrs"]:
        schema = storage["schema"]["attrs"]
        by_name = {field["variable"]: field for field in schema}
        assert by_name["type"]["schema"]["default"] == "host_path"
        path_fields = by_name["host_path_config"]["schema"]["attrs"]
        auto_permissions = next(field for field in path_fields if field["variable"] == "auto_permissions")
        assert auto_permissions["schema"]["default"] is True


def base_values() -> dict:
    return read_yaml(APP_DIR / "templates/test_values/basic-values.yaml") | read_yaml(APP_DIR / "ix_values.yaml")


def render_scenario(*, api_key: str = "", host_port: int = 15152, storage_type: str = "host_path") -> dict:
    values = copy.deepcopy(base_values())
    values["network"]["web_port"]["port_number"] = host_port
    values["abdm"]["api_key"] = api_key
    if storage_type == "ix_volume":
        values["ix_volumes"] = {
            "config": "/mnt/.ix-apps/app_mounts/abdm/config",
            "downloads": "/mnt/.ix-apps/app_mounts/abdm/downloads",
            "temp": "/mnt/.ix-apps/app_mounts/abdm/temp",
        }
        for name in ("config", "downloads", "temp"):
            values["storage"][name] = {
                "type": "ix_volume",
                "ix_volume_config": {"dataset_name": name, "create_host_path": True},
            }
    return render_compose(values)


def validate_rendered(compose: dict, *, api_key: str, host_port: int) -> None:
    services = compose["services"]
    app = services["abdm"]
    assert app["environment"]["HOME"] == "/config"
    assert app["environment"]["ABDM_DOWNLOAD_FOLDER"] == "/downloads"
    assert app["environment"]["ABDM_API_PORT"] == "15151"
    assert app["shm_size"] == "1024M"
    assert "ABDM_API_KEY" not in app["environment"] if not api_key else app["environment"]["ABDM_API_KEY"] == api_key
    assert any(p["published"] == host_port and p["target"] == 15151 for p in app["ports"])
    mounts = {volume["target"]: volume for volume in app["volumes"]}
    assert set(mounts) == {"/config", "/downloads", "/temp"}
    if all(mounts[path]["type"] == "bind" for path in mounts):
        assert mounts["/config"]["source"]
        assert mounts["/downloads"]["source"]
        assert mounts["/temp"]["source"]
    assert "permissions" in services, "Automatic dataset permission service was not rendered"
    permissions = services["permissions"]
    action_config = compose["configs"]["permissions_actions_data"]["content"]
    actions = json.loads(action_config)
    assert {a["identifier"] for a in actions} == {"config", "downloads", "temp"}
    assert all(a["uid"] == 568 and a["gid"] == 568 for a in actions)
    assert all(a["chmod"] == "0770" for a in actions)


def run_validation() -> None:
    assert_catalog_files()
    validate_rendered(render_scenario(), api_key="", host_port=15152)
    validate_rendered(render_scenario(api_key="test-api-key", host_port=18555), api_key="test-api-key", host_port=18555)
    validate_rendered(render_scenario(storage_type="ix_volume"), api_key="", host_port=15152)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-files-only", action="store_true", help="Validate catalog YAML without rendering")
    args = parser.parse_args()
    try:
        assert_catalog_files()
        if not args.check_files_only:
            run_validation()
    except Exception as error:
        print(f"ABDM catalog validation failed: {error}", file=sys.stderr)
        return 1
    print("ABDM TrueNAS 25.10 catalog files and Compose template validated successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
