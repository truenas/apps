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

    def test_custom_port_and_optional_api_key_render(self):
        validate.validate_rendered(
            validate.render_scenario(api_key="test-api-key", host_port=18555),
            api_key="test-api-key",
            host_port=18555,
        )

    def test_ix_volumes_still_render(self):
        validate.validate_rendered(validate.render_scenario(storage_type="ix_volume"), api_key="", host_port=15152)


if __name__ == "__main__":
    unittest.main()
