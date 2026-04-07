import inspect
import logging
from pprint import pformat
from typing import Any

try:
    from pydantic import BaseModel
except ImportError:
    BaseModel = None  # type: ignore[assignment, misc]


class PprintLogger:
    """A logger wrapper that adds pprint support to standard logging methods."""

    def __init__(self, logger: logging.Logger):
        self._logger = logger

    def _format_message(self, msg: Any, pprint: bool = True) -> str:
        """Format a message, optionally using pprint.

        If the message is a Pydantic model and pprint=True, uses model_dump_json()
        to show the model's internals. Otherwise uses pformat for complex objects
        or str() for simple conversion.
        """
        if not pprint:
            return str(msg)

        # Check if it's a Pydantic model
        if BaseModel is not None and isinstance(msg, BaseModel):
            return msg.model_dump_json(indent=2)

        # Use pformat for other complex objects
        return pformat(msg, width=120, depth=None)

    def debug(self, msg: Any, *args, pprint: bool = True, **kwargs) -> None:
        """Log a debug message with optional pprint formatting."""
        formatted_msg = self._format_message(msg, pprint=pprint)
        self._logger.debug(formatted_msg, *args, stacklevel=2, **kwargs)

    def info(self, msg: Any, *args, pprint: bool = True, **kwargs) -> None:
        """Log an info message with optional pprint formatting."""
        formatted_msg = self._format_message(msg, pprint=pprint)
        self._logger.info(formatted_msg, *args, stacklevel=2, **kwargs)

    def warning(self, msg: Any, *args, pprint: bool = True, **kwargs) -> None:
        """Log a warning message with optional pprint formatting."""
        formatted_msg = self._format_message(msg, pprint=pprint)
        self._logger.warning(formatted_msg, *args, stacklevel=2, **kwargs)

    def error(self, msg: Any, *args, pprint: bool = True, **kwargs) -> None:
        """Log an error message with optional pprint formatting."""
        formatted_msg = self._format_message(msg, pprint=pprint)
        self._logger.error(formatted_msg, *args, stacklevel=2, **kwargs)

    def critical(self, msg: Any, *args, pprint: bool = True, **kwargs) -> None:
        """Log a critical message with optional pprint formatting."""
        formatted_msg = self._format_message(msg, pprint=pprint)
        self._logger.critical(formatted_msg, *args, stacklevel=2, **kwargs)

    def exception(self, msg: Any, *args, pprint: bool = True, **kwargs) -> None:
        """Log an exception message with optional pprint formatting."""
        formatted_msg = self._format_message(msg, pprint=pprint)
        self._logger.exception(formatted_msg, *args, stacklevel=2, **kwargs)

    # Delegate other standard logger methods/attributes
    def __getattr__(self, name: str) -> Any:
        """Delegate any other attributes to the underlying logger."""
        return getattr(self._logger, name)


def setup_logging(level: int = logging.INFO) -> PprintLogger:
    """Set up logging and return a PprintLogger instance."""
    frame = inspect.currentframe().f_back  # type: ignore[union-attr]
    logger_name = frame.f_code.co_name  # type: ignore[union-attr]
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(level)
        formatter = logging.Formatter("%(asctime)s - %(pathname)s:%(lineno)d - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return PprintLogger(logger)
