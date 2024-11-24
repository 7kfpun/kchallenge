"""
Marvel gRPC server.
"""

from concurrent import futures
import logging
import threading
import grpc
import dotenv

from marvel.proto import marvel_pb2_grpc
from services.marvel_service import MarvelService
from tasks.marvel_task import MarvelTask
from tasks.cache_stats_task import CacheStatsTask
from utils.logging import configure_logging
from utils.worker import Worker

# Load environment variables
dotenv.load_dotenv()

# Configure logger
logger = logging.getLogger(__name__)


def start_worker(task_class, interval):
    """Start a worker for a specific task."""
    worker = Worker(task_class=task_class, retry_limit=3, interval=interval)
    worker.run()


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
    # Start workers in separate threads
    marvel_worker_thread = threading.Thread(
        target=start_worker, args=(MarvelTask, 60), daemon=True
    )
    cache_stats_worker_thread = threading.Thread(
        target=start_worker, args=(CacheStatsTask, 10), daemon=True
    )

    marvel_worker_thread.start()
    cache_stats_worker_thread.start()

    # Start gRPC server
    serve()
