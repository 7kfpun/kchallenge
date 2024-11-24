"""
WorkerManager: Manages workers and dispatches tasks.
"""

import threading
import logging
import time
from queue import Queue
from utils.worker import Worker

logger = logging.getLogger(__name__)


class WorkerManager:
    """
    Manages a pool of workers to process tasks from a shared queue.
    """

    def __init__(self, num_workers=3, interval=10, max_queue_size=100):
        """
        :param num_workers: Number of workers to manage.
        :param interval: Time interval (in seconds) to enqueue tasks.
        :param max_queue_size: Maximum size of the task queue.
        """
        self.num_workers = num_workers
        self.interval = interval
        self.task_queue = Queue(maxsize=max_queue_size)
        self.running = True
        self.workers = []
        self.condition = threading.Condition()

    def run(self, task_dispatcher):
        """
        Start the worker manager and enqueue tasks periodically.
        :param task_dispatcher: Function to map task names to executable functions.
        """
        logger.info("[Manager] Starting WorkerManager...")
        self.start_workers(task_dispatcher)

        while self.running:
            try:
                with self.condition:
                    logger.info("[Manager] Enqueuing tasks...")
                    self.enqueue_tasks()
                    self.condition.notify_all()
                    self.condition.wait(self.interval)
            except Exception as e:
                logger.error("[Manager] Error during task enqueuing: %s", e)

    def start_workers(self, task_dispatcher):
        """
        Start worker threads.
        :param task_dispatcher: Function to map task names to executable functions.
        """
        for i in range(self.num_workers):
            worker = Worker(self.task_queue, worker_id=i + 1, retry_limit=3)
            thread = threading.Thread(
                target=worker.run, args=(task_dispatcher,), daemon=True
            )
            self.workers.append(worker)
            thread.start()
            logger.info("[Manager] Worker-%d started.", i + 1)

    def enqueue_tasks(self):
        """
        Enqueue tasks from all registered enqueue functions.
        """
        for enqueue_func in self.enqueue_functions:
            enqueue_func(self.task_queue)

    def stop(self):
        """
        Stop all workers and the manager.
        """
        logger.info("[Manager] Stopping WorkerManager...")
        self.running = False
        for worker in self.workers:
            worker.stop()
