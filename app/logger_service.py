import logging
import time
import threading
from datetime import datetime, timezone

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

stop_logging = False


def periodic_warning_logs():
    warning_count = 1
    logger.info("logs nivel warning")

    while not stop_logging:
        time.sleep(10)
        if not stop_logging:
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            logger.warning(f"warning #{warning_count} at {timestamp}")
            warning_count += 1


def periodic_error_logs():
    error_count = 1
    logger.info("logs nivel error")

    while not stop_logging:
        time.sleep(20)
        if not stop_logging:
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            logger.error(f"error #{error_count} at {timestamp}")
            error_count += 1


def start_background_logging():
    logger.info("log nivel info start")
    warning_thread = threading.Thread(target=periodic_warning_logs, daemon=True)
    warning_thread.start()

    error_thread = threading.Thread(target=periodic_error_logs, daemon=True)
    error_thread.start()

    logger.info("log nivel info end")
