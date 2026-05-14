from collections import defaultdict
from collections import deque
from threading import Lock
from time import monotonic


COMPILE_LIMIT_PER_IP = 120
EXECUTION_LIMIT_PER_USER = 30
EXECUTION_LIMIT_PER_IP = 120


class FixedWindowRateLimiter:
    def __init__(self, window_seconds: int = 60, clock=monotonic) -> None:
        self._window_seconds = window_seconds
        self._clock = clock
        self._lock = Lock()
        self._events = defaultdict(deque)

    def allow(self, key: str, limit: int) -> tuple[bool, int]:
        now = self._clock()
        with self._lock:
            events = self._events[key]
            while events and now - events[0] >= self._window_seconds:
                events.popleft()
            if len(events) >= limit:
                retry_after = max(1, int(self._window_seconds - (now - events[0])))
                return False, retry_after
            events.append(now)
            return True, 0


default_rate_limiter = FixedWindowRateLimiter()


def _client_key(scope: str, identifier: str) -> str:
    return f"{scope}:{identifier}"


def allow_compile_request(ip_address: str):
    return default_rate_limiter.allow(_client_key("compile:ip", ip_address), COMPILE_LIMIT_PER_IP)


def allow_execution_request(user_id: str, ip_address: str):
    user_allowed, user_retry_after = default_rate_limiter.allow(
        _client_key("execution:user", user_id), EXECUTION_LIMIT_PER_USER
    )
    ip_allowed, ip_retry_after = default_rate_limiter.allow(
        _client_key("execution:ip", ip_address), EXECUTION_LIMIT_PER_IP
    )
    if user_allowed and ip_allowed:
        return True, 0
    retry_after = max(user_retry_after, ip_retry_after)
    return False, retry_after
