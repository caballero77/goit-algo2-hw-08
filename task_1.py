import random
import timeit

class Node:
    def __init__(self, key, value):
        self.data = (key, value)
        self.next = None
        self.prev = None

class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def push(self, key, value):
        new_node = Node(key, value)
        new_node.next = self.head
        if self.head:
            self.head.prev = new_node
        else:
            self.tail = new_node
        self.head = new_node
        return new_node

    def remove(self, node):
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next
        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev
        node.prev = None
        node.next = None

    def move_to_front(self, node):
        if node != self.head:
            self.remove(node)
            node.next = self.head
            self.head.prev = node
            self.head = node

    def remove_last(self):
        if self.tail:
            last = self.tail
            self.remove(last)
            return last
        return None

class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}
        self.list = DoublyLinkedList()

    def contains(self, key):
        return key in self.cache

    def get(self, key):
        if key in self.cache:
            node = self.cache[key]
            self.list.move_to_front(node)
            return node.data[1]
        return -1

    def put(self, key, value):
        if key in self.cache:
            node = self.cache[key]
            node.data = (key, value)
            self.list.move_to_front(node)
        else:
            if len(self.cache) >= self.capacity:
                last = self.list.remove_last()
                if last:
                    del self.cache[last.data[0]]
            new_node = self.list.push(key, value)
            self.cache[key] = new_node

    def delete(self, key):
        if key in self.cache:
            node = self.cache[key]
            self.list.remove(node)
            del self.cache[key]

def range_sum_no_cache(array, left, right):
    return sum(array[left : right + 1])

def update_no_cache(array, index, value):
    array[index] = value

def range_sum_with_cache(cache, array, left, right):
    key = (left, right)
    if cache.contains(key):
        return cache.get(key)
    result = sum(array[left : right + 1])
    cache.put(key, result)
    return result


def update_with_cache(cache, array, index, value):
    array[index] = value

    keys_to_remove = []
    for l, r in cache.cache.keys():
        if l <= index <= r:
            keys_to_remove.append((l, r))
    for key in keys_to_remove:
        cache.delete(key)

def run_no_cache(array, queries):
    arr = array.copy()
    for q in queries:
        if q[0] == "Range":
            range_sum_no_cache(arr, q[1], q[2])
        else:
            update_no_cache(arr, q[1], q[2])


def run_with_cache(array, queries):
    arr = array.copy()
    cache = LRUCache(1000)
    for q in queries:
        if q[0] == "Range":
            range_sum_with_cache(cache, arr, q[1], q[2])
        else:
            update_with_cache(cache, arr, q[1], q[2])

def make_queries(n, q, hot_pool=30, p_hot=0.95, p_update=0.03):
    hot = [(random.randint(0, n//2), random.randint(n//2, n-1))
           for _ in range(hot_pool)]
    queries = []
    for _ in range(q):
        if random.random() < p_update:        # ~3% запитів — Update
            idx = random.randint(0, n-1)
            val = random.randint(1, 100)
            queries.append(("Update", idx, val))
        else:                                 # ~97% — Range
            if random.random() < p_hot:       # 95% — «гарячі» діапазони
                left, right = random.choice(hot)
            else:                             # 5% — випадкові діапазони
                left = random.randint(0, n-1)
                right = random.randint(left, n-1)
            queries.append(("Range", left, right))
    return queries

if __name__ == "__main__":
    N = 100000
    Q = 50000
    array = [random.randint(1, N // 10) for _ in range(N)]
    queries = make_queries(N, Q)

    time_without_cache = timeit.timeit(lambda: run_no_cache(array, queries), number=1)
    time_with_cache = timeit.timeit(lambda: run_with_cache(array, queries), number=1)

    print(f"Time without cache: {time_without_cache:.4f} seconds")
    print(f"Time with cache: {time_with_cache:.4f} seconds")