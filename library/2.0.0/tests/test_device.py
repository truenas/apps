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


def test_add_device(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.devices.add_device("/h/dev/sda", "/c/dev/sda")
    c1.devices.add_device("/h/dev/sdb", "/c/dev/sdb", "rwm")
    output = render.render()
    assert output["services"]["test_container"]["devices"] == ["/h/dev/sda:/c/dev/sda", "/h/dev/sdb:/c/dev/sdb:rwm"]


def test_devices_without_host(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    with pytest.raises(Exception):
        c1.devices.add_device("", "/c/dev/sda")


def test_devices_without_container(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    with pytest.raises(Exception):
        c1.devices.add_device("/h/dev/sda", "")


def test_add_duplicate_device(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.devices.add_device("/h/dev/sda", "/c/dev/sda")
    with pytest.raises(Exception):
        c1.devices.add_device("/h/dev/sda", "/c/dev/sda")


def test_add_device_with_invalid_path(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    with pytest.raises(Exception):
        c1.devices.add_device("/h/dev/sda", "c/dev/sda")
    with pytest.raises(Exception):
        c1.devices.add_device("h/dev/sda", "/c/dev/sda")


def test_add_disallowed_device(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    with pytest.raises(Exception):
        c1.devices.add_device("/dev/dri", "/c/dev/sda")


def test_add_device_with_invalid_cgroup_perm(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    with pytest.raises(Exception):
        c1.devices.add_device("/h/dev/sda", "/c/dev/sda", "invalid")


def test_automatically_add_gpu_devices(mock_values):
    mock_values["resources"] = {"gpus": {"use_all_gpus": True}}
    render = Render(mock_values)
    render.add_container("test_container", "test_image")
    output = render.render()
    assert output["services"]["test_container"]["devices"] == ["/dev/dri:/dev/dri"]