"""
Runtime loader for the domain-specific IngestPipeline implementation.

The pipeline class is specified via the INGEST_PIPELINE_CLASS environment
variable as a dotted import path, e.g.::

    INGEST_PIPELINE_CLASS=medlit.pipeline.MedlitPipeline

The class must be a concrete subclass of
:class:`kgserver.pipeline_interface.IngestPipeline`.

If the variable is unset or the import fails, callers receive a clear
error at the point of use rather than at server startup.
"""

import importlib
import logging
import os
from typing import Optional

from pipeline_interface import IngestPipeline

logger = logging.getLogger(__name__)

_pipeline_instance: Optional[IngestPipeline] = None


def get_pipeline() -> IngestPipeline:
    """
    Return the singleton IngestPipeline instance.

    The implementation class is loaded from the INGEST_PIPELINE_CLASS
    environment variable on first call and cached for subsequent calls.

    Raises
    ------
    RuntimeError
        If INGEST_PIPELINE_CLASS is not set or the class cannot be loaded.
    TypeError
        If the loaded class is not a subclass of IngestPipeline.
    """
    global _pipeline_instance
    if _pipeline_instance is not None:
        return _pipeline_instance

    class_path = os.environ.get("INGEST_PIPELINE_CLASS", "").strip()
    if not class_path:
        raise RuntimeError(
            "INGEST_PIPELINE_CLASS environment variable is not set. "
            "Set it to the dotted import path of a concrete IngestPipeline subclass, "
            "e.g. INGEST_PIPELINE_CLASS=medlit.pipeline.MedlitPipeline"
        )

    module_path, _, class_name = class_path.rpartition(".")
    if not module_path:
        raise RuntimeError(f"INGEST_PIPELINE_CLASS={class_path!r} must be a dotted path including " "module and class, e.g. 'medlit.pipeline.MedlitPipeline'")

    try:
        module = importlib.import_module(module_path)
    except ImportError as exc:
        raise RuntimeError(f"Could not import module {module_path!r} from INGEST_PIPELINE_CLASS={class_path!r}. " "Ensure the domain pipeline package is installed.") from exc

    cls = getattr(module, class_name, None)
    if cls is None:
        raise RuntimeError(f"Module {module_path!r} has no attribute {class_name!r} " f"(INGEST_PIPELINE_CLASS={class_path!r}).")

    if not (isinstance(cls, type) and issubclass(cls, IngestPipeline)):
        raise TypeError(f"{class_path!r} is not a subclass of IngestPipeline.")

    logger.info("Loaded ingest pipeline: %s", class_path)
    _pipeline_instance = cls()
    return _pipeline_instance


def reset_pipeline() -> None:
    """
    Clear the cached pipeline instance.

    Intended for use in tests that need to swap implementations between cases.
    """
    global _pipeline_instance
    _pipeline_instance = None
