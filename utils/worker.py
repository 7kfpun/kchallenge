import logging
import time

logger = logging.getLogger(__name__)


class Worker:
    """
    Generic worker to process tasks at intervals and handle retries.
    """

    def __init__(self, task_class, retry_limit=3, interval=60):
        """
        :param task_class: The task class to execute (must implement `execute_task`).
        :param retry_limit: Maximum retries for a task.
        :param interval: Time in seconds between task executions.
        """
        self.task_class = task_class
        self.retry_limit = retry_limit
        self.interval = interval
        self.running = True

    def run(self):
        """
        Start the worker process.
        """
        logger.info("[Worker] Starting worker for task: %s", self.task_class.__name__)
        while self.running:
            self.process_tasks()
            if self.running:  # Check `running` before sleeping
                logger.info("[Worker] Sleeping for %s seconds...", self.interval)
                time.sleep(self.interval)

    def process_tasks(self):
        """
        Process all tasks with retry logic or execute single-task actions.
        """
        if hasattr(self.task_class, "get_tasks"):
            tasks = self.task_class.get_tasks()
            for task_key in tasks:
                self._execute_with_retries(task_key)
        else:
            self._execute_with_retries(None)

    def _execute_with_retries(self, task_key):
        """
        Execute a task with retries.
        """
        retry_count = 0
        success = False

        while retry_count < self.retry_limit and not success:
            if not self.running:  # Stop retries if the worker is stopped
                break
            try:
                self.task_class.execute_task(task_key)
                success = True
            except Exception as e:
                retry_count += 1
                logger.warning(
                    "[Worker] Retry %s/%s for task %s due to error: %s",
                    retry_count,
                    self.retry_limit,
                    task_key,
                    e,
                )

        if not success and self.running:
            logger.error(
                "[Worker] Task %s failed after %s retries.", task_key, self.retry_limit
            )

    def stop(self):
        """
        Stop the worker gracefully.
        """
        self.running = False
        logger.info("[Worker] Stopping worker...")
