try:
    from .error import RenderError
    from .formatter import escape_dollar
except ImportError:
    from error import RenderError
    from formatter import escape_dollar


class Healthcheck:
    def __init__(self, render_instance):
        self._render_instance = render_instance
        self._test: str | list[str] = ""
        self._interval_sec: int = 10
        self._timeout_sec: int = 5
        self._retries: int = 30
        self._start_period_sec: int = 10
        self._disabled: bool = False

    def _get_test(self):
        if isinstance(self._test, str):
            return escape_dollar(self._test)

        return [escape_dollar(t) for t in self._test]

    def disable_healthcheck(self):
        self._disabled = True

    def set_custom_test(self, test: str | list[str]):
        self._test = test

    def set_interval(self, interval: int):
        self._interval_sec = interval

    def set_timeout(self, timeout: int):
        self._timeout_sec = timeout

    def set_retries(self, retries: int):
        self._retries = retries

    def set_start_period(self, start_period: int):
        self._start_period_sec = start_period

    def render(self):
        if self._disabled:
            return {"disabled": True}

        if not self._test:
            raise RenderError("Healthcheck test is not set")

        return {
            "test": self._get_test(),
            "interval": f"{self._interval_sec}s",
            "timeout": f"{self._timeout_sec}s",
            "retries": self._retries,
            "start_period": f"{self._start_period_sec}s",
        }
