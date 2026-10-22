import json
import sys
import unittest
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_DIR))
import validate  # noqa: E402


class AbdmCatalogTests(unittest.TestCase):
    def test_catalog_files_are_well_formed_for_25_10(self):
        validate.assert_catalog_files()

    def test_install_questions_offer_dataset_selection_and_automatic_permissions(self):
        questions = validate.read_yaml(APP_DIR / "questions.yaml")
        storage = next(q for q in questions["questions"] if q["variable"] == "storage")
        for item in storage["schema"]["attrs"]:
            self.assertEqual(item["schema"]["attrs"][0]["schema"]["default"], "host_path")
            fields = {field["variable"]: field for field in item["schema"]["attrs"]}
            permissions = next(field for field in fields["host_path_config"]["schema"]["attrs"] if field["variable"] == "auto_permissions")
            self.assertTrue(permissions["schema"]["default"])

    def test_default_render_persists_selected_datasets_and_permissions(self):
        validate.validate_rendered(validate.render_scenario(), api_key="", host_port=15152)

    def test_each_selected_dataset_mounts_to_its_persistent_path_and_gets_permissions(self):
        selected = {
            "config": "/mnt/pool-a/abdm/config-data",
            "downloads": "/mnt/pool-b/finished-downloads",
            "temp": "/mnt/pool-a/abdm/workspace",
        }
        compose = validate.render_scenario(storage_paths=selected, uid=1500, gid=1600)
        validate.validate_rendered(
            compose,
            api_key="",
            host_port=15152,
            storage_paths=selected,
            uid=1500,
            gid=1600,
        )
        app_mounts = {volume["target"]: volume["source"] for volume in compose["services"]["abdm"]["volumes"]}
        self.assertEqual(app_mounts, {
            "/config": selected["config"],
            "/downloads": selected["downloads"],
            "/temp": selected["temp"],
        })
        actions = json.loads(compose["configs"]["permissions_actions_data"]["content"])
        permissions = {action["identifier"]: action for action in actions}
        permission_mounts = {volume["target"]: volume["source"] for volume in compose["services"]["permissions"]["volumes"]}
        for name, path in selected.items():
            with self.subTest(dataset=name):
                action = permissions[name]
                self.assertEqual(action["uid"], 1500)
                self.assertEqual(action["gid"], 1600)
                self.assertEqual(action["chmod"], "0770")
                self.assertEqual(permission_mounts[action["mount_path"]], path)

    def test_custom_port_and_optional_api_key_render(self):
        validate.validate_rendered(
            validate.render_scenario(api_key="test-api-key", host_port=18555),
            api_key="test-api-key",
            host_port=18555,
        )

    def test_ix_volumes_still_render(self):
        validate.validate_rendered(validate.render_scenario(storage_type="ix_volume"), api_key="", host_port=15152, storage_type="ix_volume")


if __name__ == "__main__":
    unittest.main()
