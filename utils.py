from collections import defaultdict
from discord import log_to_discord
from test_log import log
import heapq
import random


class ExploreQueue:
    """A queue that keeps a max capacity AND has a heap"""

    def __init__(self, items=[], max_capacity=1e7, max_buffer=300, test=False):
        self.max = max_capacity
        self.max_buffer = max_buffer
        self.test = test

        self._counts = defaultdict(int)
        for i in items:
            self.append(i)

    def append(self, item):
        self._counts[item] += 1

    def pop(self, i=0):
        h = [(-count, item) for item, count in self._counts.items()]
        heapq.heapify(h)
        count, item = heapq.heappop(h)
        log("popped count of", -count)
        if not self.test:
            log_to_discord("Popped", item, "with a count of", count)
        self._counts[item] = 0
        return item

    def estimate_free(self):
        current_size = len(self._counts)
        remaining = (self.max - current_size) / (current_size + 1) ** 0.7
        return min(int(remaining), self.max_buffer)

    def __len__(self):
        return len(self._counts)


def test_explore():
    explore_queue = ExploreQueue([1], max_buffer=20, max_capacity=2e3, test=True)

    t = 0
    while t < 1000:
        t += 1
        c = explore_queue.pop(0)
        buffer = explore_queue.estimate_free()
        for i in range(buffer):
            r = random.randint(0, 2000)
            explore_queue.append(r)
        log(f"{t} {buffer} Queee length {len(explore_queue)}")


if __name__ == "__main__":
    test_explore()
