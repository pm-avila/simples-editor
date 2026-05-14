import unittest

from backend.rate_limit import FixedWindowRateLimiter


class FixedWindowRateLimiterTest(unittest.TestCase):
    def test_rejects_after_limit_is_reached(self):
        clock = [0.0]
        limiter = FixedWindowRateLimiter(window_seconds=60, clock=lambda: clock[0])

        for _ in range(30):
            allowed, retry_after = limiter.allow("user-123", 30)
            self.assertTrue(allowed)
            self.assertEqual(retry_after, 0)

        allowed, retry_after = limiter.allow("user-123", 30)
        self.assertFalse(allowed)
        self.assertEqual(retry_after, 60)

    def test_window_expires_and_allows_new_requests(self):
        clock = [0.0]
        limiter = FixedWindowRateLimiter(window_seconds=60, clock=lambda: clock[0])

        for _ in range(30):
            limiter.allow("ip-1", 30)

        self.assertFalse(limiter.allow("ip-1", 30)[0])
        clock[0] = 61.0
        allowed, retry_after = limiter.allow("ip-1", 30)
        self.assertTrue(allowed)
        self.assertEqual(retry_after, 0)


if __name__ == "__main__":
    unittest.main()
