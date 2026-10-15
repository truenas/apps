import pytest

from base.error import RenderError
from base.render import Render


@pytest.mark.parametrize(
    "line",
    [
        pytest.param("FROM test_image", id="build_image_with_from"),
        pytest.param(" FROM test_image", id="build_image_with_from_with_whitespace"),
    ],
)
def test_build_image_with_from(c1, line):
    with pytest.raises(RenderError, match=r"FROM cannot be used in build image"):
        c1.build_image([line])


def test_build_image(render, c1):
    c1.build_image(["RUN echo hello", None, "", "RUN echo world", "RUN echo $MY_VAR > /tmp/test.txt"])
    output = render.render()
    assert (
        output["services"]["test_container"]["image"]
        == "ix-nginx:latest_bb420e21d704f6aaaa9c671c4698cc4ae1a004333bd74780911cd7df6918487b"
    )
    assert output["services"]["test_container"]["build"] == {
        "tags": ["ix-nginx:latest_bb420e21d704f6aaaa9c671c4698cc4ae1a004333bd74780911cd7df6918487b"],
        "dockerfile_inline": """FROM nginx:latest
RUN echo hello
RUN echo world
RUN echo $$MY_VAR > /tmp/test.txt
""",
    }


def test_build_image_with_digest_pin(mock_values):
    mock_values["images"]["test_image"]["tag"] = "1.27.0@sha256:1234567890"
    render = Render(mock_values)
    c1 = render.add_container("test_container", "test_image")
    c1.healthcheck.disable()
    c1.build_image(["RUN echo hello"])
    output = render.render()
    assert (
        output["services"]["test_container"]["image"]
        == "ix-nginx:1.27.0_1b657c223e9f0e3f42827639424e13275c580f5e94d193b205d6eae6596199ed"
    )
    assert output["services"]["test_container"]["build"] == {
        "tags": ["ix-nginx:1.27.0_1b657c223e9f0e3f42827639424e13275c580f5e94d193b205d6eae6596199ed"],
        "dockerfile_inline": """FROM nginx:1.27.0@sha256:1234567890
RUN echo hello
""",
    }


def test_build_image_digest_change_changes_tag(mock_values):
    images = []
    for digest in ["sha256:1111111111", "sha256:2222222222"]:
        mock_values["images"]["test_image"]["tag"] = f"1.27.0@{digest}"
        render = Render(mock_values)
        c1 = render.add_container("test_container", "test_image")
        c1.healthcheck.disable()
        c1.build_image(["RUN echo hello"])
        images.append(render.render()["services"]["test_container"]["image"])
    assert images[0] != images[1]
