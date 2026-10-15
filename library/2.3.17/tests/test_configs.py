import pytest

from base.error import RenderError


def test_add_duplicate_config_with_different_data(c1):
    c1.configs.add("test_config", "test_data", "/some/path")
    with pytest.raises(RenderError, match=r"Config \[test_config\] already added with different data"):
        c1.configs.add("test_config", "test_data2", "/some/path")


@pytest.mark.parametrize(
    "data, target, match",
    [
        pytest.param(
            "test_data",
            "",
            r"Expected \[target\] to be set for config \[test_config\]",
            id="add_config_with_empty_target",
        ),
        pytest.param(
            "",
            "/some/path",
            r"Expected \[data\] to be non-empty for config \[test_config\]",
            id="add_config_with_empty_data",
        ),
    ],
)
def test_add_config_with_empty_field(c1, data, target, match):
    with pytest.raises(RenderError, match=match):
        c1.configs.add("test_config", data, target)


def test_add_duplicate_target(c1):
    c1.configs.add("test_config", "test_data", "/some/path")
    with pytest.raises(RenderError, match=r"Target \[/some/path\] already used for another config"):
        c1.configs.add("test_config2", "test_data2", "/some/path")


def test_add_config(render, c1):
    c1.configs.add("test_config", "$test_data", "/some/path")
    output = render.render()
    assert output["configs"]["test_config"]["content"] == "$$test_data"
    assert output["services"]["test_container"]["configs"] == [{"source": "test_config", "target": "/some/path"}]


def test_add_config_with_mode(render, c1):
    c1.configs.add("test_config", "test_data", "/some/path", "0777")
    output = render.render()
    assert output["configs"]["test_config"]["content"] == "test_data"
    assert output["services"]["test_container"]["configs"] == [
        {"source": "test_config", "target": "/some/path", "mode": 511}
    ]
