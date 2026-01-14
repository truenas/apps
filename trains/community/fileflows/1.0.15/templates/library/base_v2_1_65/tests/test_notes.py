import pytest


from render import Render


@pytest.fixture
def mock_values():
    return {
        "ix_context": {
            "app_metadata": {
                "name": "test_app",
                "title": "Test App",
                "train": "enterprise",
            }
        },
        "images": {
            "test_image": {
                "repository": "nginx",
                "tag": "latest",
            }
        },
    }


def test_notes(mock_values):
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    output = render.render()
    assert (
        output["x-notes"]
        == """# Test App

## Security

**Read the following security precautions to ensure that you wish to continue using this application.**

---

### Container: [test_container]

#### Running user/group(s)

- User: unknown
- Group: unknown
- Supplementary Groups: apps

---

## Bug Reports and Feature Requests

If you find a bug in this app or have an idea for a new feature, please file an issue at
https://ixsystems.atlassian.net
"""
    )


def test_notes_on_non_enterprise_train(mock_values):
    mock_values["ix_context"]["app_metadata"]["train"] = "community"
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.set_user(568, 568)
    c1.healthcheck.disable()
    output = render.render()
    assert (
        output["x-notes"]
        == """# Test App

## Security

**Read the following security precautions to ensure that you wish to continue using this application.**

---

### Container: [test_container]

#### Running user/group(s)

- User: 568
- Group: 568
- Supplementary Groups: apps

---

## Bug Reports and Feature Requests

If you find a bug in this app or have an idea for a new feature, please file an issue at
https://github.com/truenas/apps
"""
    )


def test_notes_with_warnings(mock_values):
    render = Render(mock_values)
    render.notes.add_warning("this is not properly configured. fix it now!")
    render.notes.add_warning("that is not properly configured. fix it later!")
    c1 = render.add_container("test_container", "test_image")
    c1.set_user(568, 568)
    c1.healthcheck.disable()
    output = render.render()
    assert (
        output["x-notes"]
        == """# Test App

## Warnings

- this is not properly configured. fix it now!
- that is not properly configured. fix it later!

## Security

**Read the following security precautions to ensure that you wish to continue using this application.**

---

### Container: [test_container]

#### Running user/group(s)

- User: 568
- Group: 568
- Supplementary Groups: apps

---

## Bug Reports and Feature Requests

If you find a bug in this app or have an idea for a new feature, please file an issue at
https://ixsystems.atlassian.net
"""
    )


def test_notes_with_deprecations(mock_values):
    render = Render(mock_values)
    render.notes.add_deprecation("this is will be removed later. fix it now!")
    render.notes.add_deprecation("that is will be removed later. fix it later!")
    c1 = render.add_container("test_container", "test_image")
    c1.set_user(568, 568)
    c1.healthcheck.disable()
    output = render.render()
    assert (
        output["x-notes"]
        == """# Test App

## Deprecations

- this is will be removed later. fix it now!
- that is will be removed later. fix it later!

## Security

**Read the following security precautions to ensure that you wish to continue using this application.**

---

### Container: [test_container]

#### Running user/group(s)

- User: 568
- Group: 568
- Supplementary Groups: apps

---

## Bug Reports and Feature Requests

If you find a bug in this app or have an idea for a new feature, please file an issue at
https://ixsystems.atlassian.net
"""
    )


def test_notes_with_body(mock_values):
    render = Render(mock_values)
    render.notes.set_body(
        """## Additional info

Some info
some other info.
"""
    )
    c1 = render.add_container("test_container", "test_image")
    c1.set_user(568, 568)
    c1.healthcheck.disable()
    output = render.render()
    assert (
        output["x-notes"]
        == """# Test App

## Security

**Read the following security precautions to ensure that you wish to continue using this application.**

---

### Container: [test_container]

#### Running user/group(s)

- User: 568
- Group: 568
- Supplementary Groups: apps

---

## Additional info

Some info
some other info.

## Bug Reports and Feature Requests

If you find a bug in this app or have an idea for a new feature, please file an issue at
https://ixsystems.atlassian.net
"""
    )


def test_notes_all(mock_values):
    render = Render(mock_values)
    render.notes.add_warning("this is not properly configured. fix it now!")
    render.notes.add_warning("that is not properly configured. fix it later!")
    render.notes.add_deprecation("this is will be removed later. fix it now!")
    render.notes.add_deprecation("that is will be removed later. fix it later!")
    render.notes.add_info("some info")
    render.notes.add_info("some other info")
    render.notes.set_body(
        """## Additional info

Some info
some other info.
"""
    )
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    c1.set_privileged(True)
    c1.set_user(0, 0)
    c1.add_group(0)
    c1.set_ipc_mode("host")
    c1.set_pid_mode("host")
    c1.set_cgroup("host")
    c1.set_tty(True)
    c1.remove_security_opt("no-new-privileges")
    c1.add_docker_socket()
    c1.add_tun_device()
    c1.add_usb_bus()
    c1.add_snd_device()
    c1.devices.add_device("/dev/null", "/dev/null", "rwm")
    c1.add_storage("/etc/os-release", {"type": "host_path", "host_path_config": {"path": "/etc/os-release"}})
    c1.restart.set_policy("on-failure", 1)

    c2 = render.add_container("test_container2", "test_image")
    c2.healthcheck.disable()
    c2.set_user(568, 568)

    c3 = render.add_container("test_container3", "test_image")
    c3.healthcheck.disable()
    c3.restart.set_policy("on-failure", 1)
    c3.set_user(568, 568)

    output = render.render()
    assert (
        output["x-notes"]
        == """# Test App

## Warnings

- Container [test_container] is running with a TTY, Logs do not appear correctly in the UI due to an [upstream bug](https://github.com/docker/docker-py/issues/1394)
- this is not properly configured. fix it now!
- that is not properly configured. fix it later!

## Deprecations

- this is will be removed later. fix it now!
- that is will be removed later. fix it later!

## Info

- some info
- some other info

## Security

**Read the following security precautions to ensure that you wish to continue using this application.**

---

### Container: [test_container2]

#### Running user/group(s)

- User: 568
- Group: 568
- Supplementary Groups: apps

---

### Container: [test_container]

**This container is short-lived.**

#### Privileged mode is enabled

- Has the same level of control as a system administrator
- Can access and modify any part of your TrueNAS system

#### Running user/group(s)

- User: root
- Group: root
- Supplementary Groups: apps, audio, docker, root

#### Host IPC namespace is enabled

- Container can access the inter-process communication mechanisms of the host
- Allows communication with other processes on the host under particular circumstances

#### Host PID namespace is enabled

- Container can see and interact with all host processes
- Potential for privilege escalation or process manipulation

#### Host cgroup namespace is enabled

- Container shares control groups with the host system
- Can bypass resource limits and isolation boundaries

#### Security option [no-new-privileges] is not set

- Processes can gain additional privileges through setuid/setgid binaries
- Can potentially allow privilege escalation attacks within the container

#### Passing Host Files, Devices, or Sockets into the Container

- /dev/null - (rwm)
- Docker Socket (/var/run/docker.sock) - (Read Only)
- OS Release File (/etc/os-release) - (Read/Write)
- Sound Device (/dev/snd) - (Read/Write)
- TUN Device (/dev/net/tun) - (Read/Write)
- USB Devices (/dev/bus/usb) - (Read/Write)

---

### Container: [test_container3]

**This container is short-lived.**

#### Running user/group(s)

- User: 568
- Group: 568
- Supplementary Groups: apps

---

## Additional info

Some info
some other info.

## Bug Reports and Feature Requests

If you find a bug in this app or have an idea for a new feature, please file an issue at
https://ixsystems.atlassian.net
"""  # noqa
    )
