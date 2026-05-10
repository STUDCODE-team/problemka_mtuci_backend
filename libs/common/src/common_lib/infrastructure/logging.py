from __future__ import annotations

import json
import logging
import sys

from loguru import logger

from common_lib.utils.trace import current_trace_id


def setup_logging(service_name: str) -> None:
    def json_sink(message) -> None:
        record = message.record
        entry: dict = {
            "timestamp": record["time"].isoformat(),
            "level": record["level"].name,
            "service": service_name,
            "trace_id": current_trace_id(),
            "logger": record["name"],
            "message": record["message"],
        }
        if record["exception"]:
            entry["exception"] = str(record["exception"])
        print(json.dumps(entry), file=sys.stdout, flush=True)

    logger.remove()
    logger.add(json_sink, level="INFO", backtrace=False, diagnose=False)

    class _InterceptHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno  # type: ignore[assignment]

            frame, depth = logging.currentframe(), 2
            while frame and frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back  # type: ignore[assignment]
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(
                level, record.getMessage()
            )

    logging.basicConfig(handlers=[_InterceptHandler()], level=0, force=True)
    for name in list(logging.root.manager.loggerDict):
        log = logging.getLogger(name)
        log.handlers = []
        log.propagate = True
