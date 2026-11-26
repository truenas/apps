from typing import Protocol

from .render import Render


class Lib(Protocol):
    """What apps can use through the `lib` passed to their render(lib, values)."""

    Render: type[Render]


__all__ = ["Lib", "Render"]
