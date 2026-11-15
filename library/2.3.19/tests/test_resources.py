import pytest


from base.error import RenderError
from base.render import Render


def test_automatically_add_cpu(mock_values):
    mock_values["resources"] = {"limits": {"cpus": 1.0}}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    output = render.render()
    assert output["services"]["test_container"]["deploy"]["resources"]["limits"]["cpus"] == "1.0"


def test_invalid_cpu(mock_values):
    mock_values["resources"] = {"limits": {"cpus": "invalid"}}
    render = Render(mock_values)
    with pytest.raises(RenderError, match=r"Expected cpus to be a number or a float \(minimum 1\.0\), got \[invalid\]"):
        render.add_container("test_container", "test_image")


def test_automatically_add_memory(mock_values):
    mock_values["resources"] = {"limits": {"memory": 1024}}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    output = render.render()
    assert output["services"]["test_container"]["deploy"]["resources"]["limits"]["memory"] == "1024M"


def test_invalid_memory(mock_values):
    mock_values["resources"] = {"limits": {"memory": "invalid"}}
    render = Render(mock_values)
    with pytest.raises(RenderError, match=r"Expected memory to be a number, got \[invalid\]"):
        render.add_container("test_container", "test_image")


def test_automatically_add_gpus(mock_values):
    mock_values["resources"] = {
        "gpus": {
            "nvidia_gpu_selection": {
                "pci_slot_0": {"uuid": "uuid_0", "use_gpu": True},
                "pci_slot_1": {"uuid": "uuid_1", "use_gpu": True},
            },
        }
    }
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    output = render.render()
    devices = output["services"]["test_container"]["deploy"]["resources"]["reservations"]["devices"]
    assert len(devices) == 1
    assert devices[0] == {
        "capabilities": ["gpu"],
        "driver": "nvidia",
        "device_ids": ["uuid_0", "uuid_1"],
    }
    assert output["services"]["test_container"]["group_add"] == [44, 107, 568]


def test_gpu_without_uuid(mock_values):
    mock_values["resources"] = {
        "gpus": {
            "nvidia_gpu_selection": {
                "pci_slot_0": {"uuid": "", "use_gpu": True},
                "pci_slot_1": {"uuid": "uuid_1", "use_gpu": True},
            },
        }
    }
    render = Render(mock_values)
    with pytest.raises(RenderError, match=r"Expected \[uuid\] to be set for GPU in slot \[pci_slot_0\]"):
        render.add_container("test_container", "test_image")


def test_remove_cpus_and_memory_with_gpus(mock_values):
    mock_values["resources"] = {"gpus": {"nvidia_gpu_selection": {"pci_slot_0": {"uuid": "uuid_1", "use_gpu": True}}}}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    c1.deploy.resources.remove_cpus_and_memory()
    output = render.render()
    assert "limits" not in output["services"]["test_container"]["deploy"]["resources"]
    devices = output["services"]["test_container"]["deploy"]["resources"]["reservations"]["devices"]
    assert len(devices) == 1
    assert devices[0] == {
        "capabilities": ["gpu"],
        "driver": "nvidia",
        "device_ids": ["uuid_1"],
    }


def test_remove_cpus_and_memory(render, c1):
    c1.deploy.resources.remove_cpus_and_memory()
    output = render.render()
    assert "deploy" not in output["services"]["test_container"]


def test_remove_devices(mock_values):
    mock_values["resources"] = {"gpus": {"nvidia_gpu_selection": {"pci_slot_0": {"uuid": "uuid_0", "use_gpu": True}}}}
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    c1.deploy.resources.remove_devices()
    output = render.render()
    assert "reservations" not in output["services"]["test_container"]["deploy"]["resources"]
    assert output["services"]["test_container"]["group_add"] == [568]


def test_set_profile(render, c1):
    c1.deploy.resources.set_profile("low")
    output = render.render()
    assert output["services"]["test_container"]["deploy"]["resources"]["limits"]["cpus"] == "1"
    assert output["services"]["test_container"]["deploy"]["resources"]["limits"]["memory"] == "512M"


def test_set_profile_invalid_profile(c1):
    with pytest.raises(RenderError, match=r"Resource profile \[invalid_profile\] is not valid"):
        c1.deploy.resources.set_profile("invalid_profile")
