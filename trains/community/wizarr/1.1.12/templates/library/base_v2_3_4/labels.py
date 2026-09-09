try:
    from .error import RenderError
    from .formatter import escape_dollar
    from .validations import valid_label_key_or_raise
except ImportError:
    from error import RenderError
    from formatter import escape_dollar
    from validations import valid_label_key_or_raise


class Labels:
    def __init__(self):
        self._labels: dict[str, str] = {}

    def add_label(self, key: str, value: str):
        key = valid_label_key_or_raise(key)

        if key in self._labels.keys():
            raise RenderError(f"Label [{key}] already added")

        self._labels[key] = escape_dollar(str(value))

    def has_labels(self) -> bool:
        return bool(self._labels)

    def render(self) -> dict[str, str]:
        if not self.has_labels():
            return {}
        return {label: value for label, value in sorted(self._labels.items())}
