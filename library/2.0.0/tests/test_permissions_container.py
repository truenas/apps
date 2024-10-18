import pytest


from render import Render


@pytest.fixture
def mock_values():
    return {
        "images": {
            "test_image": {
                "repository": "nginx",
                "tag": "latest",
            }
        },
    }


def test_no_permissions_container_added(mock_values):
    render = Render(mock_values)
    # render["permissions_actions"] = {}  # This will be on the render instance
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    vol_config = {"type": "volume", "volume_config": {"volume_name": "test_volume"}, "auto_permissions": False}
    c1.add_storage("/some/path", vol_config, {"uid": 1000, "gid": 1000, "mode": "check"})
    if render.has_permissions_actions():
        c1.depends.add_dependency(render.permissions_container_name(), "service_completed_successfully")
    output = render.render()
    assert "configs" not in output
    assert "ix-permissions" not in output["services"]
    assert "depends_on" not in output["services"]["test_container"]


def test_permissions_container_added(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()

    c2 = render.add_container("test_container2", "test_image")
    c2.healthcheck.disable()

    vol_config = {"type": "volume", "volume_config": {"volume_name": "test_volume"}, "auto_permissions": True}
    c1.add_storage("/some/path", vol_config, {"uid": 1000, "gid": 1000, "mode": "check"})
    c2.add_storage("/some/path", vol_config, {"uid": 1000, "gid": 1000, "mode": "check"})
    vol_config2 = {"type": "volume", "volume_config": {"volume_name": "test_volume2"}, "auto_permissions": True}
    c2.add_storage("/some/path2", vol_config2, {"uid": 1001, "gid": 1001, "mode": "check"})

    if render.has_permissions_actions():
        c1.depends.add_dependency(render.permissions_container_name(), "service_completed_successfully")
        c2.depends.add_dependency(render.permissions_container_name(), "service_completed_successfully")
    output = render.render()
    assert output["services"]["test_container"]["depends_on"] == {
        render.permissions_container_name(): {"condition": "service_completed_successfully"}
    }
    assert output["services"]["test_container"]["depends_on"] == {
        render.permissions_container_name(): {"condition": "service_completed_successfully"}
    }
    assert output["configs"]["permissions_run_script"]["content"] != ""
    assert (
        output["configs"]["permissions_actions_data"]["content"]
        == '[{"mount_path": "/mnt/permissions/test_volume", "source": "test_volume", "mode": "check", "uid": 1000, "gid": 1000, "chmod": null, "is_temporary": false}, {"mount_path": "/mnt/permissions/test_volume2", "source": "test_volume2", "mode": "check", "uid": 1001, "gid": 1001, "chmod": null, "is_temporary": false}]'  # noqa
    )
    perms_container = output["services"][render.permissions_container_name()]
    assert perms_container["volumes"] == [
        {
            "type": "volume",
            "source": "test_volume",
            "target": "/mnt/permissions/test_volume",
            "read_only": False,
            "volume": {"nocopy": False},
        },
        {
            "type": "volume",
            "source": "test_volume2",
            "target": "/mnt/permissions/test_volume2",
            "read_only": False,
            "volume": {"nocopy": False},
        },
    ]
    assert perms_container["configs"] == [
        {"source": "permissions_actions_data", "target": "/script/actions.json", "mode": 320},
        {"source": "permissions_run_script", "target": "/script/run.py", "mode": 448},
    ]


def test_permissions_container_different_config_for_same_volume(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()

    c2 = render.add_container("test_container2", "test_image")
    c2.healthcheck.disable()

    vol_config = {"type": "volume", "volume_config": {"volume_name": "test_volume"}, "auto_permissions": True}
    c1.add_storage("/some/path", vol_config, {"uid": 1000, "gid": 1000, "mode": "check"})
    with pytest.raises(Exception):
        c2.add_storage("/some/path", vol_config, {"uid": 1001, "gid": 1001, "mode": "check"})


def test_permissions_container_invalid_is_temporary(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()

    c2 = render.add_container("test_container2", "test_image")
    c2.healthcheck.disable()

    vol_config = {"type": "volume", "volume_config": {"volume_name": "test_volume"}, "auto_permissions": True}
    with pytest.raises(Exception):
        c1.add_storage("/some/path", vol_config, {"uid": 1000, "gid": 1000, "mode": "check", "is_temporary": "yes"})


def test_permissions_container_missing_uid(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()

    c2 = render.add_container("test_container2", "test_image")
    c2.healthcheck.disable()

    vol_config = {"type": "volume", "volume_config": {"volume_name": "test_volume"}, "auto_permissions": True}
    with pytest.raises(Exception):
        c1.add_storage("/some/path", vol_config, {"uid": "", "gid": 1000, "mode": "check"})


def test_permissions_container_missing_gid(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()

    c2 = render.add_container("test_container2", "test_image")
    c2.healthcheck.disable()

    vol_config = {"type": "volume", "volume_config": {"volume_name": "test_volume"}, "auto_permissions": True}
    with pytest.raises(Exception):
        c1.add_storage("/some/path", vol_config, {"uid": 1000, "gid": "", "mode": "check"})


def test_permissions_container_invalid_mode(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()

    c2 = render.add_container("test_container2", "test_image")
    c2.healthcheck.disable()

    vol_config = {"type": "volume", "volume_config": {"volume_name": "test_volume"}, "auto_permissions": True}
    with pytest.raises(Exception):
        c1.add_storage("/some/path", vol_config, {"uid": 1000, "gid": 1000, "mode": "invalid"})
