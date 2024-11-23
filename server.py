from concurrent import futures
from dotenv import load_dotenv
from marvel.proto import marvel_pb2_grpc
from services.marvel_service import MarvelService
from utils.logging import configure_logging

import threading
import time
from services.marvel_service import cache

import grpc
import logging

# Load environment variables
load_dotenv()

# Configure logger
logger = logging.getLogger(__name__)


def log_cache_stats():
    while True:
        stats = cache.stats()
        print(f"Cache Stats: {stats}")
        time.sleep(10)  # Log every 10 seconds (it should be longer in production)


stats_thread = threading.Thread(target=log_cache_stats, daemon=True)
stats_thread.start()


def serve():
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
    serve()
