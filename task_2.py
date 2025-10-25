import random
from typing import Dict
import time
from collections import deque

class SlidingWindowRateLimiter:
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.window_size = window_size
        self.max_per_user_requests = max_requests
        self.user_messages: Dict[str, deque] = {}

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        if user_id not in self.user_messages:
            return

        window = self.user_messages[user_id]
        while len(window) > 0 and current_time - window[0] > self.window_size:
            window.popleft()

        if len(window) == 0:
            del self.user_messages[user_id]

    def can_send_message(self, user_id: str) -> bool:
        self._cleanup_window(user_id, time.time())

        return True if user_id not in self.user_messages \
            else len(self.user_messages[user_id]) < self.max_per_user_requests

    def record_message(self, user_id: str) -> bool:
        if not self.can_send_message(user_id):
            return False

        if user_id not in self.user_messages:
            self.user_messages[user_id] = deque()

        self.user_messages[user_id].append(time.time())
        return True

    def time_until_next_allowed(self, user_id: str) -> float:
        current_time = time.time()
        self._cleanup_window(user_id, current_time)

        if user_id not in self.user_messages:
            return 0.0
        if len(self.user_messages[user_id]) < self.max_per_user_requests:
            return 0.0

        return max(0.0,
                   (self.user_messages[user_id][0] + self.window_size) - current_time)

def test_rate_limiter():
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    print("\\n=== Симуляція потоку повідомлень ===")
    for message_id in range(1, 11):
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")

        time.sleep(random.uniform(0.1, 1.0))

    print("\\nОчікуємо 4 секунди...")
    time.sleep(4)

    print("\\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")

        time.sleep(random.uniform(0.1, 1.0))

if __name__ == "__main__":
    test_rate_limiter()