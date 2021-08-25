from test_log import log


class ExploreQueue:
    """A queue that keeps a max capacity"""

    def __init__(self, init=[], max_capacity=1e7):
        self.q = init
        self.max = max_capacity

    def append(self, item):
        self.q.append(item)

    def pop(self, i=0):
        return self.q.pop(i)

    def estimate_free(self):
        remaining = (self.max - len(self.q)) / (len(self.q) + 1) ** 0.7
        return min(int(remaining), 300)

    def __len__(self):
        return len(self.q)


def test_explore():
    explore_queue = ExploreQueue([1])

    t = 0
    while True:
        t += 1
        c = explore_queue.pop(0)
        buffer = explore_queue.estimate_free()
        for i in range(buffer):
            explore_queue.append(1)
        log(f"{t} {buffer} Queee length {len(explore_queue)}")


if __name__ == "__main__":
    test_explore()
