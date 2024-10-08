try:
    from .validations import must_be_valid_restart_policy
except ImportError:
    from validations import must_be_valid_restart_policy


class RestartPolicy:
    def __init__(self, render_instance):
        self._render_instance = render_instance
        self._policy: str = "unless-stopped"
        self._maximum_retry_count: int = 0

    def set_policy(self, policy: str, maximum_retry_count: int = 0):
        must_be_valid_restart_policy(policy, maximum_retry_count)
        self._policy = policy
        self._maximum_retry_count = maximum_retry_count

    def render(self):
        if self._policy == "on-failure" and self._maximum_retry_count > 0:
            return f"{self._policy}:{self._maximum_retry_count}"
        return self._policy
