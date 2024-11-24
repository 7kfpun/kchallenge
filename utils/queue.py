"""
A simple thread-safe in-memory queue for tasks.
Replace this implementation with an external queue like SQS, Redis, or a database.
"""

import threading


class SimpleQueue:
    """
    A simple thread-safe in-memory queue for tasks.
    """

    def __init__(self):
        self.queue = []
        self.lock = threading.Lock()

    def push(self, task):
        """
        Add a task to the queue.
        """
        with self.lock:
            self.queue.append(task)

    def pop(self):
        """
        Retrieve and remove a task from the queue.
        Returns None if the queue is empty.
        """
        with self.lock:
            if self.queue:
                return self.queue.pop(0)
            return None

    def size(self):
        """
        Return the number of tasks in the queue.
        """
        with self.lock:
            return len(self.queue)
