"""
Marvel gRPC server and periodic task execution.
"""

import asyncio
import logging

import grpc
from app.grpc_services.proto.marvel_pb2_grpc import add_MarvelServiceServicer_to_server
from app.grpc_services.marvel_service import MarvelService
from app.tasks.marvel_task import enqueue_marvel_tasks
from app.tasks.cache_stats_task import log_cache_stats
from app.utils.logging import configure_logging

logger = logging.getLogger(__name__)


async def periodic_task_runner():
    """
    Periodically run tasks for cache updates and statistics logging.
    """
    while True:
        logger.info("[Periodic Task] Enqueueing and executing tasks...")
        await enqueue_marvel_tasks.kiq()
        await log_cache_stats.kiq()
        await asyncio.sleep(20)


async def start_grpc_server():
    """
    Start the gRPC server.
    """
    server = grpc.aio.server()
    add_MarvelServiceServicer_to_server(MarvelService(), server)
    server.add_insecure_port("[::]:50051")
    await server.start()
    await server.wait_for_termination()


async def main():
    """
    Main function to start gRPC server and periodic task runner.
    """
    configure_logging()
    await asyncio.gather(
        start_grpc_server(),
        periodic_task_runner(),
    )


if __name__ == "__main__":
    asyncio.run(main())
