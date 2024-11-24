"""
Marvel gRPC server with worker manager.
"""

from concurrent import futures
import logging
import threading
import grpc
import dotenv

from marvel.proto import marvel_pb2_grpc
from services.marvel_service import MarvelService
from utils.manager import WorkerManager
from tasks.marvel_task import MarvelTask
from tasks.cache_stats_task import CacheStatsTask
from utils.logging import configure_logging

# Load environment variables
dotenv.load_dotenv()

# Configure logger
logger = logging.getLogger(__name__)


def serve():
    """Serve the gRPC server."""
    configure_logging()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    marvel_pb2_grpc.add_MarvelServiceServicer_to_server(MarvelService(), server)
    server.add_insecure_port("[::]:50051")
    logger.info("gRPC server is starting on port 50051")
    server.start()
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("gRPC server is shutting down")


if __name__ == "__main__":
    # Configure logging
    configure_logging()

    # Initialize WorkerManager
    manager = WorkerManager(num_workers=3, interval=10)

    # Register enqueue functions
    manager.enqueue_functions = [MarvelTask.enqueue_tasks, CacheStatsTask.enqueue_tasks]

    # Define task dispatcher
    task_dispatcher = lambda task: {
        "marvel_task": MarvelTask.execute_task,
        "cache_stats": CacheStatsTask.execute_task,
    }.get(
        task["task_name"],
        lambda _: logger.warning("[Manager] Unknown task: %s", task["task_name"]),
    )

    # Start WorkerManager in a separate thread
    manager_thread = threading.Thread(
        target=manager.run, args=(task_dispatcher,), daemon=True
    )
    manager_thread.start()

    # Start gRPC server
    try:
        serve()
    finally:
        # Stop the manager gracefully
        manager.stop()
