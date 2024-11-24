"""
Worker: Generic worker to process tasks from a shared queue with retry logic.
"""

import logging
import time

logger = logging.getLogger(__name__)


class Worker:
    """
    A worker that processes tasks from a shared queue with retry logic.
    """

    def __init__(self, task_queue, worker_id=1, retry_limit=3):
        """
        Initialize the worker.
        :param task_queue: The queue holding tasks to process.
        :param worker_id: Unique identifier for the worker.
        :param retry_limit: Number of retries allowed for a task.
        """
        self.task_queue = task_queue
        self.worker_id = worker_id
        self.retry_limit = retry_limit
        self.running = True

    def run(self, task_dispatcher):
        """
        Continuously fetch and process tasks from the queue.
        :param task_dispatcher: Function to map task keys to executable functions.
        """
        logger.info("[Worker-%d] Starting worker...", self.worker_id)
        while self.running:
            if not self.task_queue.empty():
                task_key = self.task_queue.get()
                task_function = task_dispatcher(task_key)
                if task_function:
                    self._execute_with_retries(task_function, task_key)
                else:
                    logger.warning(
                        "[Worker-%d] No function for task: %s", self.worker_id, task_key
                    )
            else:
                time.sleep(1)

    def _execute_with_retries(self, task_function, task_data):
        """
        Execute a task with retry logic.
        :param task_function: Function to execute the task.
        :param task_data: Data for the task to process.
        """
        for attempt in range(1, self.retry_limit + 1):
            try:
                task_function(task_data)
                return
            except Exception as e:
                logger.warning(
                    "[Worker-%d] Attempt %d failed for task %s: %s",
                    self.worker_id,
                    attempt,
                    task_data,
                    e,
                )
        logger.error(
            "[Worker-%d] Task %s failed after %d attempts.",
            self.worker_id,
            task_data,
            self.retry_limit,
        )

    def stop(self):
        """Stop the worker gracefully."""
        self.running = False
        logger.info("[Worker-%d] Stopping worker...", self.worker_id)
