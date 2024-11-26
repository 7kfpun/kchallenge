"""
Logging module for the application.
"""

import logging


def configure_logging():
    """
    Configure logging for the application.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
