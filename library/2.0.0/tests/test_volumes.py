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


def test_add_volume_invalid_type(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable_healthcheck()
    with pytest.raises(Exception):
        render.volumes.add_volume("test_volume", {"type": "invalid_type"})


def test_add_volume_empty_identifier(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable_healthcheck()
    with pytest.raises(Exception):
        render.volumes.add_volume("", {})


def test_add_volume_duplicate_identifier(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable_healthcheck()
    render.volumes.add_volume("test_volume", {"type": "host_path", "host_path_config": {"path": "/mnt/test"}})
    with pytest.raises(Exception):
        render.volumes.add_volume("test_volume", {"type": "host_path", "host_path_config": {"path": "/mnt/test"}})


def test_add_volume_host_path_invalid_propagation(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable_healthcheck()
    render.volumes.add_volume(
        "test_volume",
        {"type": "host_path", "host_path_config": {"path": "/mnt/test", "propagation": "invalid_propagation"}},
    )
    with pytest.raises(Exception):
        c1.volume_mounts.add_volume_mount("test_volume", "/some/path")


def test_add_host_path_volume_no_host_path_config(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable_healthcheck()
    with pytest.raises(Exception):
        render.volumes.add_volume("test_volume", {"type": "host_path"})


def test_add_host_path_volume_no_path(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable_healthcheck()
    with pytest.raises(Exception):
        render.volumes.add_volume("test_volume", {"type": "host_path", "host_path_config": {}})


def test_add_host_path_volume_mount(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable_healthcheck()
    render.volumes.add_volume("test_volume", {"type": "host_path", "host_path_config": {"path": "/mnt/test"}})
    c1.volume_mounts.add_volume_mount("test_volume", "/some/path")
    output = render.render()
    assert output["services"]["test_container"]["volumes"] == [
        {
            "type": "bind",
            "source": "/mnt/test",
            "target": "/some/path",
            "read_only": False,
            "bind": {"create_host_path": False, "propagation": "rprivate"},
        }
    ]


def test_add_host_path_volume_mount_with_acl(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable_healthcheck()
    render.volumes.add_volume(
        "test_volume",
        {
            "type": "host_path",
            "host_path_config": {
                "path": "/mnt/test",  # should be ignored
                "acl_enable": True,
                "acl": {
                    "path": "/mnt/test/acl",
                },
            },
        },
    )
    c1.volume_mounts.add_volume_mount("test_volume", "/some/path")
    output = render.render()
    assert output["services"]["test_container"]["volumes"] == [
        {
            "type": "bind",
            "source": "/mnt/test/acl",
            "target": "/some/path",
            "read_only": False,
            "bind": {"create_host_path": False, "propagation": "rprivate"},
        }
    ]


def test_add_host_path_volume_mount_with_propagation(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable_healthcheck()
    render.volumes.add_volume(
        "test_volume",
        {"type": "host_path", "host_path_config": {"path": "/mnt/test", "propagation": "slave"}},
    )
    c1.volume_mounts.add_volume_mount("test_volume", "/some/path")
    output = render.render()
    assert output["services"]["test_container"]["volumes"] == [
        {
            "type": "bind",
            "source": "/mnt/test",
            "target": "/some/path",
            "read_only": False,
            "bind": {"create_host_path": False, "propagation": "slave"},
        }
    ]


def test_add_host_path_volume_mount_with_create_host_path(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable_healthcheck()
    render.volumes.add_volume(
        "test_volume",
        {"type": "host_path", "host_path_config": {"path": "/mnt/test", "create_host_path": True}},
    )
    c1.volume_mounts.add_volume_mount("test_volume", "/some/path")
    output = render.render()
    assert output["services"]["test_container"]["volumes"] == [
        {
            "type": "bind",
            "source": "/mnt/test",
            "target": "/some/path",
            "read_only": False,
            "bind": {"create_host_path": True, "propagation": "rprivate"},
        }
    ]


def test_add_host_path_volume_mount_with_read_only(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable_healthcheck()
    render.volumes.add_volume(
        "test_volume",
        {
            "type": "host_path",
            "read_only": True,
            "host_path_config": {
                "path": "/mnt/test",
            },
        },
    )
    c1.volume_mounts.add_volume_mount("test_volume", "/some/path")
    output = render.render()
    assert output["services"]["test_container"]["volumes"] == [
        {
            "type": "bind",
            "source": "/mnt/test",
            "target": "/some/path",
            "read_only": True,
            "bind": {"create_host_path": False, "propagation": "rprivate"},
        }
    ]


def test_add_ix_volume_invalid_dataset_name(mock_values):
    mock_values["ix_volumes"] = {"test_dataset": "/mnt/test"}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable_healthcheck()
    with pytest.raises(Exception):
        render.volumes.add_volume(
            "test_volume",
            {
                "type": "ix_volume",
                "ix_volume_config": {
                    "dataset_name": "invalid_dataset",
                },
            },
        )


def test_add_ix_volume_no_ix_volume_config(mock_values):
    mock_values["ix_volumes"] = {"test_dataset": "/mnt/test"}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable_healthcheck()
    with pytest.raises(Exception):
        render.volumes.add_volume("test_volume", {"type": "ix_volume"})


def test_add_ix_volume_volume_mount(mock_values):
    mock_values["ix_volumes"] = {"test_dataset": "/mnt/test"}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable_healthcheck()
    render.volumes.add_volume(
        "test_volume",
        {
            "type": "ix_volume",
            "ix_volume_config": {
                "dataset_name": "test_dataset",
            },
        },
    )
    c1.volume_mounts.add_volume_mount("test_volume", "/some/path")
    output = render.render()
    assert output["services"]["test_container"]["volumes"] == [
        {
            "type": "bind",
            "source": "/mnt/test",
            "target": "/some/path",
            "read_only": False,
            "bind": {"create_host_path": False, "propagation": "rprivate"},
        }
    ]


def test_add_ix_volume_volume_mount_with_options(mock_values):
    mock_values["ix_volumes"] = {"test_dataset": "/mnt/test"}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable_healthcheck()
    render.volumes.add_volume(
        "test_volume",
        {
            "type": "ix_volume",
            "ix_volume_config": {
                "dataset_name": "test_dataset",
                "propagation": "rslave",
                "create_host_path": True,
            },
        },
    )
    c1.volume_mounts.add_volume_mount("test_volume", "/some/path")
    output = render.render()
    assert output["services"]["test_container"]["volumes"] == [
        {
            "type": "bind",
            "source": "/mnt/test",
            "target": "/some/path",
            "read_only": False,
            "bind": {"create_host_path": True, "propagation": "rslave"},
        }
    ]


def test_add_volumes_with_duplicate_target(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable_healthcheck()
    render.volumes.add_volume("test_volume", {"type": "host_path", "host_path_config": {"path": "/mnt/test"}})
    render.volumes.add_volume("test_volume2", {"type": "host_path", "host_path_config": {"path": "/mnt/test"}})
    c1.volume_mounts.add_volume_mount("test_volume", "/some/path")
    with pytest.raises(Exception):
        c1.volume_mounts.add_volume_mount("test_volume2", "/some/path")
