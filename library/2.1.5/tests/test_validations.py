import pytest
import tempfile

from pathlib import Path
from validations import is_allowed_path, RESTRICTED, RESTRICTED_IN


@pytest.fixture
def tmp_path():
    """Creates a temporary directory and returns it as a pathlib.Path."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.mark.parametrize(
    "test_path, expected",
    [
        # Non-restricted path (should be valid)
        ("/tmp/somefile", True),
        # Exactly /mnt (restricted_in)
        ("/mnt", False),
        # Exactly / (restricted_in)
        ("/", False),
        # Subdirectory inside /mnt/.ix-apps (restricted)
        ("/mnt/.ix-apps/something", False),
        # A path that is a restricted directory exactly
        ("/home", False),
        ("/var/log", False),
        ("/mnt/.ix-apps", False),
        ("/data", False),
        # Subdirectory inside e.g. /data
        ("/data/subdir", False),
        # Not an obviously restricted path
        ("/usr/local/share", True),
        # Another system path likely not in restricted list
        ("/opt/myapp", True),
    ],
)
def test_is_allowed_path_direct(test_path, expected):
    """Test direct paths against the is_allowed_path function."""
    assert is_allowed_path(test_path) == expected


def test_is_allowed_path_symlink(tmp_path):
    """
    Test that a symlink pointing to a restricted directory is detected as invalid,
    and a symlink pointing to an allowed directory is valid.
    """
    # Create a real (allowed) directory and a restricted directory in a temp location
    allowed_dir = tmp_path / "allowed_dir"
    allowed_dir.mkdir()

    restricted_dir = tmp_path / "restricted_dir"
    restricted_dir.mkdir()

    # We will simulate that "restricted_dir" is actually a symlink link pointing to e.g. "/var/log"
    # or we create a subdir to match the restricted pattern.
    # For demonstration, let's just patch it to a path in the restricted list.
    real_restricted_path = Path("/home")  # This is one of the restricted directories

    # Create symlinks to test
    symlink_allowed = tmp_path / "symlink_allowed"
    symlink_restricted = tmp_path / "symlink_restricted"

    # Point the symlinks
    symlink_allowed.symlink_to(allowed_dir)
    symlink_restricted.symlink_to(real_restricted_path)

    assert is_allowed_path(str(symlink_allowed)) is True
    assert is_allowed_path(str(symlink_restricted)) is False


def test_is_allowed_path_nested_symlink(tmp_path):
    """
    Test that even a nested symlink that eventually resolves into restricted
    directories is seen as invalid.
    """
    # e.g., Create 2 symlinks that chain to /root
    link1 = tmp_path / "link1"
    link2 = tmp_path / "link2"

    # link2 -> /root
    link2.symlink_to(Path("/root"))
    # link1 -> link2
    link1.symlink_to(link2)

    assert is_allowed_path(str(link1)) is False


def test_is_allowed_path_nonexistent(tmp_path):
    """
    Test a path that does not exist at all. The code calls .resolve() which will
    give the absolute path, but if it's not restricted, it should still be valid.
    """
    nonexistent = tmp_path / "this_does_not_exist"
    assert is_allowed_path(str(nonexistent)) is True


@pytest.mark.parametrize(
    "test_path",
    list(RESTRICTED),
)
def test_is_allowed_path_restricted_list(test_path):
    """Test that all items in the RESTRICTED list are invalid."""
    assert is_allowed_path(test_path) is False


@pytest.mark.parametrize(
    "test_path",
    list(RESTRICTED_IN),
)
def test_is_allowed_path_restricted_in_list(test_path):
    """
    Test that items in RESTRICTED_IN are invalid.
    """
    assert is_allowed_path(test_path) is False
