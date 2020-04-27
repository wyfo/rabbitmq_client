import logging
from contextvars import ContextVar
from typing import Any, Mapping

log_record_extension: ContextVar[Mapping[str, Any]] = ContextVar(
    "log_record_extension", default={})


def add_log_record_extensions(*, _overwrite: bool = False, **kwargs):
    base = log_record_extension.get() if not _overwrite else {}
    log_record_extension.set({**base, **kwargs})


old_factory = logging.getLogRecordFactory()


def record_factory(*args, **kwargs):
    record = old_factory(*args, **kwargs)
    record.__dict__.update(log_record_extension.get())
    return record


logging.setLogRecordFactory(record_factory)
