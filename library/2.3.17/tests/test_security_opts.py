import pytest

from base.error import RenderError


def test_add_security_opt(render, c1):
    c1.add_security_opt("apparmor", "unconfined")
    output = render.render()
    assert output["services"]["test_container"]["security_opt"] == ["apparmor=unconfined", "no-new-privileges=true"]


def test_add_duplicate_security_opt(c1):
    with pytest.raises(RenderError, match=r"Security Option \[no-new-privileges\] already added"):
        c1.add_security_opt("no-new-privileges", True)


def test_add_empty_security_opt(c1):
    with pytest.raises(RenderError, match=r"Security Option \[\] is not valid"):
        c1.add_security_opt("", True)


def test_remove_security_opt(render, c1):
    c1.remove_security_opt("no-new-privileges")
    output = render.render()
    assert "security_opt" not in output["services"]["test_container"]


def test_add_security_opt_boolean(render, c1):
    c1.remove_security_opt("no-new-privileges")
    c1.add_security_opt("no-new-privileges", False)
    output = render.render()
    assert output["services"]["test_container"]["security_opt"] == ["no-new-privileges=false"]


def test_add_security_opt_arg(render, c1):
    c1.add_security_opt("label", "type", "svirt_apache_t")
    output = render.render()
    assert output["services"]["test_container"]["security_opt"] == [
        "label=type:svirt_apache_t",
        "no-new-privileges=true",
    ]


def test_add_security_opt_with_invalid_opt(c1):
    with pytest.raises(RenderError, match=r"Security Option \[invalid\] is not valid"):
        c1.add_security_opt("invalid")


def test_add_security_opt_with_opt_containing_value(c1):
    c1.remove_security_opt("no-new-privileges")
    with pytest.raises(RenderError, match=r"Security Option \[no-new-privileges=true\] cannot contain \[:\] or \[=\]"):
        c1.add_security_opt("no-new-privileges=true")
    with pytest.raises(RenderError, match=r"Security Option \[apparmor:unconfined\] cannot contain \[:\] or \[=\]"):
        c1.add_security_opt("apparmor:unconfined")
