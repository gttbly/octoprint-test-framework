import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


class WaitTimeoutError(TimeoutError):
    pass


def wait_until(
    condition: Callable[[], T],
    *,
    timeout: float,
    interval: float = 0.5,
    description: str = "condition",
) -> T:
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None

    while time.monotonic() < deadline:
        try:
            value = condition()
            if value:
                return value
        except Exception as exc:  # Polling tolerates transient transport errors.
            last_error = exc
        time.sleep(interval)

    message = f"Timed out after {timeout}s waiting for {description}"
    if last_error:
        message = f"{message}; last error: {last_error}"
    raise WaitTimeoutError(message)
