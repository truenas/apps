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

## Bug Reports and Feature Requests

If you find a bug in this app or have an idea for a new feature, please file an issue at
https://ixsystems.atlassian.net

"""
    )


def test_notes_on_non_enterprise_train(mock_values):
    mock_values["ix_context"]["app_metadata"]["train"] = "community"
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    output = render.render()
    assert (
        output["x-notes"]
        == """# Test App

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
    c1.healthcheck.disable()
    output = render.render()
    assert (
        output["x-notes"]
        == """# Test App

## Warnings

- this is not properly configured. fix it now!
- that is not properly configured. fix it later!

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
    c1.healthcheck.disable()
    output = render.render()
    assert (
        output["x-notes"]
        == """# Test App

## Deprecations

- this is will be removed later. fix it now!
- that is will be removed later. fix it later!

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
    c1.healthcheck.disable()
    output = render.render()
    assert (
        output["x-notes"]
        == """# Test App

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
    render.notes.set_body(
        """## Additional info

Some info
some other info.
"""
    )
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    output = render.render()
    assert (
        output["x-notes"]
        == """# Test App

## Warnings

- this is not properly configured. fix it now!
- that is not properly configured. fix it later!

## Deprecations

- this is will be removed later. fix it now!
- that is will be removed later. fix it later!

## Additional info

Some info
some other info.

## Bug Reports and Feature Requests

If you find a bug in this app or have an idea for a new feature, please file an issue at
https://ixsystems.atlassian.net

"""
    )
