"""Tests for the PprintLogger and setup_logging functionality.

This module verifies:
- PprintLogger wraps standard logging.Logger correctly
- pprint parameter defaults to True and formats complex objects
- pprint=False uses simple string conversion
- All log levels support pprint formatting
- Delegation to underlying logger methods works
- Simple strings work with both pprint options
- Pydantic models use model_dump_json() when pprint=True
"""

import logging
from io import StringIO

import pytest

from kgraph.pprint_logging import PprintLogger, setup_logging

try:
    from pydantic import BaseModel

    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    BaseModel = None  # type: ignore[assignment, misc]


class TestPprintLogger:
    """Tests for PprintLogger formatting and delegation."""

    def test_pprint_formats_dict(self) -> None:
        """Test that pprint=True formats dictionaries nicely."""
        logger = logging.getLogger("test")
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(StringIO())
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)

        pprint_logger = PprintLogger(logger)
        test_dict = {"key1": "value1", "key2": {"nested": "data"}}

        pprint_logger.info(test_dict, pprint=True)

        output = handler.stream.getvalue()
        assert "key1" in output
        assert "key2" in output
        assert "nested" in output
        # pprint should format with proper indentation
        assert "{" in output

    def test_pprint_false_uses_str(self) -> None:
        """Test that pprint=False uses simple string conversion."""
        logger = logging.getLogger("test")
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(StringIO())
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)

        pprint_logger = PprintLogger(logger)
        test_dict = {"key": "value"}

        pprint_logger.info(test_dict, pprint=False)

        output = handler.stream.getvalue()
        # Should contain the dict representation but not necessarily formatted
        assert "key" in output or str(test_dict) in output

    def test_pprint_defaults_to_true(self) -> None:
        """Test that pprint parameter defaults to True."""
        logger = logging.getLogger("test")
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(StringIO())
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)

        pprint_logger = PprintLogger(logger)
        test_list = [1, 2, 3, {"nested": "data"}]

        # Don't specify pprint, should default to True
        pprint_logger.info(test_list)

        output = handler.stream.getvalue()
        # Should be formatted with pprint
        assert "[" in output
        assert "nested" in output

    def test_simple_string_with_pprint(self) -> None:
        """Test that simple strings work with pprint=True."""
        logger = logging.getLogger("test")
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(StringIO())
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)

        pprint_logger = PprintLogger(logger)
        simple_msg = "Simple message"

        pprint_logger.info(simple_msg, pprint=True)

        output = handler.stream.getvalue()
        assert "Simple message" in output

    def test_all_log_levels_support_pprint(self) -> None:
        """Test that all log levels (debug, info, warning, error, critical) support pprint."""
        logger = logging.getLogger("test_all_levels")
        logger.setLevel(logging.DEBUG)
        # Clear any existing handlers
        logger.handlers.clear()
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        pprint_logger = PprintLogger(logger)
        test_data = {"level": "test"}

        pprint_logger.debug(test_data, pprint=True)
        pprint_logger.info(test_data, pprint=True)
        pprint_logger.warning(test_data, pprint=True)
        pprint_logger.error(test_data, pprint=True)
        pprint_logger.critical(test_data, pprint=True)

        output = stream.getvalue()
        assert "DEBUG" in output
        assert "INFO" in output
        assert "WARNING" in output
        assert "ERROR" in output
        assert "CRITICAL" in output
        # Also verify the data was formatted
        assert "level" in output
        assert "test" in output

    def test_exception_logging(self) -> None:
        """Test that exception logging works with pprint."""
        logger = logging.getLogger("test")
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(StringIO())
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)

        pprint_logger = PprintLogger(logger)
        test_data = {"error": "details"}

        try:
            raise ValueError("Test exception")
        except ValueError:
            pprint_logger.exception(test_data, pprint=True)

        output = handler.stream.getvalue()
        assert "error" in output
        assert "ValueError" in output or "Test exception" in output

    def test_delegates_to_underlying_logger(self) -> None:
        """Test that PprintLogger delegates other methods to underlying logger."""
        logger = logging.getLogger("test")
        pprint_logger = PprintLogger(logger)

        # Should be able to call standard logger methods
        pprint_logger.setLevel(logging.WARNING)
        assert logger.level == logging.WARNING

        # Should be able to access handlers
        assert hasattr(pprint_logger, "handlers")
        assert pprint_logger.handlers == logger.handlers

    def test_nested_structures_formatted(self) -> None:
        """Test that deeply nested structures are formatted correctly."""
        logger = logging.getLogger("test")
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(StringIO())
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)

        pprint_logger = PprintLogger(logger)
        nested_data = {
            "level1": {
                "level2": {
                    "level3": ["item1", "item2", {"level4": "deep"}],
                },
            },
        }

        pprint_logger.info(nested_data, pprint=True)

        output = handler.stream.getvalue()
        assert "level1" in output
        assert "level2" in output
        assert "level3" in output
        assert "level4" in output
        assert "item1" in output

    def test_list_formatting(self) -> None:
        """Test that lists are formatted nicely with pprint."""
        logger = logging.getLogger("test")
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(StringIO())
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)

        pprint_logger = PprintLogger(logger)
        test_list = [1, 2, 3, {"key": "value"}, [4, 5, 6]]

        pprint_logger.info(test_list, pprint=True)

        output = handler.stream.getvalue()
        assert "1" in output
        assert "2" in output
        assert "key" in output
        assert "value" in output

    @pytest.mark.skipif(not PYDANTIC_AVAILABLE, reason="Pydantic not available")
    def test_pydantic_model_uses_model_dump_json(self) -> None:
        """Test that Pydantic models use model_dump_json() when pprint=True."""
        logger = logging.getLogger("test")
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(StringIO())
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)

        pprint_logger = PprintLogger(logger)

        class TestModel(BaseModel):
            name: str
            age: int
            nested: dict[str, str]

        model = TestModel(name="Test", age=42, nested={"key": "value"})

        pprint_logger.info(model, pprint=True)

        output = handler.stream.getvalue()
        # Should be JSON format with indentation
        assert "name" in output
        assert "Test" in output
        assert "age" in output
        assert "42" in output
        assert "nested" in output
        assert "key" in output
        assert "value" in output
        # Should be JSON format (has quotes around string values)
        assert '"Test"' in output or '"name"' in output

    @pytest.mark.skipif(not PYDANTIC_AVAILABLE, reason="Pydantic not available")
    def test_pydantic_model_with_pprint_false(self) -> None:
        """Test that Pydantic models use str() when pprint=False."""
        logger = logging.getLogger("test")
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(StringIO())
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)

        pprint_logger = PprintLogger(logger)

        class TestModel(BaseModel):
            name: str

        model = TestModel(name="Test")

        pprint_logger.info(model, pprint=False)

        output = handler.stream.getvalue()
        # Should use standard string representation, not JSON
        assert "Test" in output or "name" in output


class TestSetupLogging:
    """Tests for setup_logging function."""

    def test_setup_logging_returns_pprint_logger(self) -> None:
        """Test that setup_logging returns a PprintLogger instance."""

        def test_function() -> PprintLogger:
            return setup_logging()

        logger = test_function()
        assert isinstance(logger, PprintLogger)

    def test_setup_logging_configures_handler(self) -> None:
        """Test that setup_logging properly configures handlers and formatters."""

        def test_function() -> PprintLogger:
            return setup_logging(level=logging.DEBUG)

        logger = test_function()
        assert len(logger.handlers) > 0
        assert logger.level == logging.DEBUG

    def test_setup_logging_uses_caller_name(self) -> None:
        """Test that setup_logging uses the calling function's name as logger name."""

        def my_test_function() -> PprintLogger:
            return setup_logging()

        logger = my_test_function()
        # The underlying logger should be named after the calling function
        assert logger.name == "my_test_function" or "my_test_function" in logger.name

    def test_setup_logging_does_not_duplicate_handlers(self) -> None:
        """Test that setup_logging doesn't add duplicate handlers on multiple calls."""

        def test_function() -> PprintLogger:
            logger1 = setup_logging()
            logger2 = setup_logging()
            # Both should return the same underlying logger instance
            assert logger1._logger is logger2._logger  # pylint: disable=protected-access
            # Should only have one handler
            assert len(logger1.handlers) == 1
            return logger1

        logger = test_function()
        assert len(logger.handlers) == 1
