import pytest
from pathlib import Path


from base.error import RenderError
from base.render import Render


def test_add_device(render, c1):
    c1.devices.add_device("/h/dev/sda", "/c/dev/sda")
    c1.devices.add_device("/h/dev/sdb", "/c/dev/sdb", "rwm")
    output = render.render()
    assert output["services"]["test_container"]["devices"] == ["/h/dev/sda:/c/dev/sda", "/h/dev/sdb:/c/dev/sdb:rwm"]


@pytest.mark.parametrize(
    "host_path, container_path, error",
    [
        pytest.param("", "/c/dev/sda", r"Path \[\] cannot be empty", id="devices_without_host"),
        pytest.param("/h/dev/sda", "", r"Path \[\] cannot be empty", id="devices_without_container"),
        pytest.param(
            "/h/dev/sda",
            "c/dev/sda",
            r"Path \[c/dev/sda\] must start with /",
            id="add_device_with_invalid_container_path",
        ),
        pytest.param(
            "h/dev/sda", "/c/dev/sda", r"Path \[h/dev/sda\] must start with /", id="add_device_with_invalid_host_path"
        ),
        pytest.param(
            "/dev/dri",
            "/c/dev/sda",
            r"Device \[/dev/dri\] is not allowed to be manually added",
            id="add_disallowed_device",
        ),
        pytest.param(
            "/dev/bus/usb",
            "/dev/bus/usb",
            r"Device \[/dev/bus/usb\] is not allowed to be manually added",
            id="add_usb_bus_disallowed",
        ),
        pytest.param("/dev/zfs", "/dev/zfs", r"Device \[/dev/zfs\] is not allowed\.", id="add_zfs_device"),
    ],
)
def test_add_invalid_device(c1, host_path, container_path, error):
    with pytest.raises(RenderError, match=error):
        c1.devices.add_device(host_path, container_path)


def test_add_zfs_device_with_allow_disallowed(c1):
    with pytest.raises(RenderError, match=r"Device \[/dev/zfs\] is not allowed\."):
        c1.devices.add_device("/dev/zfs", "/dev/zfs", allow_disallowed=True)


def test_add_zfs_device_via_symlink(c1, monkeypatch):
    # Symlinks resolve on the machine that renders, so this one is faked
    def mock_resolve(self):
        return Path("/dev/zfs") if str(self) == "/dev/zfs-link" else self

    monkeypatch.setattr(Path, "resolve", mock_resolve)
    with pytest.raises(RenderError, match=r"Device \[/dev/zfs-link\] is not allowed\."):
        c1.devices.add_device("/dev/zfs-link", "/dev/zfs")


def test_add_duplicate_device(c1):
    c1.devices.add_device("/h/dev/sda", "/c/dev/sda")
    with pytest.raises(RenderError, match=r"Device with container path \[/c/dev/sda\] already added"):
        c1.devices.add_device("/h/dev/sda", "/c/dev/sda")


def test_add_dri_disallowed_device(mock_values):
    mock_values["resources"] = {"gpus": {"use_all_gpus": True}}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    c1.devices.add_dri_device()
    output = render.render()
    assert output["services"]["test_container"]["devices"] == ["/dev/dri:/dev/dri"]


def test_add_device_with_invalid_cgroup_perm(c1):
    with pytest.raises(RenderError, match=r"Cgroup Permission \[invalid\] is not valid"):
        c1.devices.add_device("/h/dev/sda", "/c/dev/sda", "invalid")


def test_automatically_add_gpu_devices(mock_values):
    mock_values["resources"] = {"gpus": {"use_all_gpus": True}}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    output = render.render()
    assert output["services"]["test_container"]["devices"] == ["/dev/dri:/dev/dri"]
    assert output["services"]["test_container"]["group_add"] == [44, 107, 568]


def test_automatically_add_gpu_devices_and_kfd(mock_values):
    mock_values["resources"] = {"gpus": {"use_all_gpus": True, "kfd_device_exists": True}}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    output = render.render()
    assert output["services"]["test_container"]["devices"] == ["/dev/dri:/dev/dri", "/dev/kfd:/dev/kfd"]
    assert output["services"]["test_container"]["group_add"] == [44, 107, 568]


def test_remove_gpu_devices(mock_values):
    mock_values["resources"] = {"gpus": {"use_all_gpus": True}}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    c1.devices.remove_devices()
    output = render.render()
    assert "devices" not in output["services"]["test_container"]
    assert output["services"]["test_container"]["group_add"] == [568]


def test_add_usb_bus(render, c1):
    c1.devices.add_usb_bus()
    output = render.render()
    assert output["services"]["test_container"]["devices"] == ["/dev/bus/usb:/dev/bus/usb"]


def test_add_snd_device(render, c1):
    c1.add_snd_device()
    output = render.render()
    assert output["services"]["test_container"]["devices"] == ["/dev/snd:/dev/snd"]
    assert output["services"]["test_container"]["group_add"] == [29, 568]


def test_add_tun_device(render, c1):
    c1.add_tun_device()
    output = render.render()
    assert output["services"]["test_container"]["devices"] == ["/dev/net/tun:/dev/net/tun"]


def test_device_resolved_host_device(render, c1, monkeypatch):
    # Symlinks resolve on the machine that renders, so this one is faked
    def mock_resolve(self):
        return Path("/dev/sda") if str(self) == "/dev/disk/by-id/ata-disk" else self

    monkeypatch.setattr(Path, "resolve", mock_resolve)
    c1.devices.add_device("/dev/disk/by-id/ata-disk", "/dev/disk0")
    c1.devices.add_device("/dev/ttyUSB0", "/dev/ttyUSB0")
    devices = {d.host_device: d.resolved_host_device for d in c1.devices._devices}
    assert devices == {"/dev/disk/by-id/ata-disk": "/dev/sda", "/dev/ttyUSB0": "/dev/ttyUSB0"}
    # The rendered device is the path as given
    output = render.render()
    assert output["services"]["test_container"]["devices"] == [
        "/dev/disk/by-id/ata-disk:/dev/disk0",
        "/dev/ttyUSB0:/dev/ttyUSB0",
    ]
