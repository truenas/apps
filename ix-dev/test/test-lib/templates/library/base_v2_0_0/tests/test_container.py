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


def test_resolve_image(mock_values):
    render = Render(mock_values)
    render.add_container("test_container", "test_image")
    output = render.render()
    assert output["services"]["test_container"]["image"] == "nginx:latest"


def test_missing_repo(mock_values):
    mock_values["images"]["test_image"]["repository"] = ""
    render = Render(mock_values)
    with pytest.raises(Exception):
        render.add_container("test_container", "test_image")


def test_missing_tag(mock_values):
    mock_values["images"]["test_image"]["tag"] = ""
    render = Render(mock_values)
    with pytest.raises(Exception):
        render.add_container("test_container", "test_image")


def test_non_existing_image(mock_values):
    render = Render(mock_values)
    with pytest.raises(Exception):
        render.add_container("test_container", "non_existing_image")


def test_invalid_restart_policy(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    with pytest.raises(Exception):
        c1.set_restart("invalid_policy")


def test_valid_restart_policy(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.set_restart("on-failure")
    output = render.render()
    assert output["services"]["test_container"]["restart"] == "on-failure"


def test_tty(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.set_tty(True)
    output = render.render()
    assert output["services"]["test_container"]["tty"] is True


def test_stdin(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.set_stdin(True)
    output = render.render()
    assert output["services"]["test_container"]["stdin_open"] is True


def test_user(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.set_user(1000, 1000)
    output = render.render()
    assert output["services"]["test_container"]["user"] == "1000:1000"


def test_invalid_user(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    with pytest.raises(Exception):
        c1.set_user(-100, 1000)


def test_valid_caps(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.add_caps(["ALL", "NET_ADMIN"])
    output = render.render()
    assert output["services"]["test_container"]["cap_add"] == ["ALL", "NET_ADMIN"]
    assert output["services"]["test_container"]["cap_drop"] == ["ALL"]


def test_add_duplicate_caps(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    with pytest.raises(Exception):
        c1.add_caps(["ALL", "NET_ADMIN", "NET_ADMIN"])


def test_invalid_caps(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    with pytest.raises(Exception):
        c1.add_caps(["invalid_cap"])


def test_remove_security_opt(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.remove_security_opt("no-new-privileges")
    output = render.render()
    assert "security_opt" not in output["services"]["test_container"]


def test_add_security_opt(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.add_security_opt("seccomp=unconfined")
    output = render.render()
    assert output["services"]["test_container"]["security_opt"] == [
        "no-new-privileges",
        "seccomp=unconfined",
    ]


def test_add_duplicate_security_opt(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    with pytest.raises(Exception):
        c1.add_security_opt("no-new-privileges")


def test_network_mode(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.set_network_mode("host")
    output = render.render()
    assert output["services"]["test_container"]["network_mode"] == "host"


def test_network_mode_with_container(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.set_network_mode("service:test_container")
    output = render.render()
    assert output["services"]["test_container"]["network_mode"] == "service:test_container"


def test_network_mode_with_container_missing(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    with pytest.raises(Exception):
        c1.set_network_mode("service:missing_container")


def test_invalid_network_mode(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    with pytest.raises(Exception):
        c1.set_network_mode("invalid_mode")


def test_entrypoint(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.set_entrypoint(["/bin/bash", "-c", "echo hello $MY_ENV"])
    output = render.render()
    assert output["services"]["test_container"]["entrypoint"] == [
        "/bin/bash",
        "-c",
        "echo hello $$MY_ENV",
    ]


def test_command(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.set_command(["echo", "hello $MY_ENV"])
    output = render.render()
    assert output["services"]["test_container"]["command"] == ["echo", "hello $$MY_ENV"]