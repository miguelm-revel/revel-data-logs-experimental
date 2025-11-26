import logging
import inspect
from functools import wraps

from ..interfaces import _RevelFormatter

__all__ = [
    "loggable",
    "error_logs"
]

def _get_logger_base(logger: logging.Logger | logging.LoggerAdapter) -> logging.Logger:
    if isinstance(logger, logging.LoggerAdapter):
        return logger.logger
    return logger

def _assert_logger(logger: logging.Logger | logging.LoggerAdapter):
    _is_valid_logger = False
    logger_base = _get_logger_base(logger)
    for _handler in logger_base.handlers:
        if isinstance(_handler.formatter, _RevelFormatter):
            _is_valid_logger = True
            break
    assert _is_valid_logger, "logger has no valid RevelFormatter"

def _get_args(signature, args, kwargs):
    bound = signature.bind(*args, **kwargs)
    bound.apply_defaults()

    return dict(bound.arguments)

def loggable(logger: logging.Logger | logging.LoggerAdapter):
    """Decorator factory that logs calls to the decorated function.

        The resulting decorator emits an ``INFO`` record every time the
        wrapped function is called. The log message has the form
        ``"func <name> called"`` and the bound arguments are included in the
        structured ``extra`` payload under the ``"args"`` key.

        The ``logger`` must ultimately be backed by a handler whose formatter
        implements the REVEL ``_RevelFormatter`` protocol, otherwise an
        ``AssertionError`` is raised.

        Args:
            logger: Logger or logger adapter configured with a REVEL formatter.

        Returns:
            A decorator that can be applied to any callable. The decorated
            function preserves its original signature and return value.
    """

    _assert_logger(logger)

    def decorator(func):
        signature = inspect.signature(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            arg_dict = _get_args(signature, args, kwargs)

            logger.info(f"func {func.__name__} called", extra={"extra": {"args": arg_dict}})

            return func(*args, **kwargs)

        return wrapper
    return decorator


def error_logs(logger: logging.Logger | logging.LoggerAdapter, handle_error: bool = True):
    """Decorator factory that logs errors raised by the decorated function.

        The resulting decorator wraps the function in a ``try/except`` block.
        If the function raises an exception, an ``ERROR`` log is emitted using
        the exception message as ``message`` and including both the function
        name and bound arguments in the structured ``extra`` payload.

        Behavior after logging depends on ``handle_error``:

          * When ``handle_error`` is ``True`` (the default), the exception is
            swallowed and the wrapper returns ``None``.
          * When ``handle_error`` is ``False``, the original exception is
            re-raised after logging.

        As with :func:`loggable`, the provided ``logger`` must ultimately use a
        REVEL formatter or an ``AssertionError`` will be raised.

        Args:
            logger: Logger or logger adapter configured with a REVEL formatter.
            handle_error: Whether to swallow exceptions after logging them.

        Returns:
            A decorator that can be applied to any callable. On success, the
            decorated function's return value is passed through unchanged.
    """
    _assert_logger(logger)

    def decorator(func):
        signature = inspect.signature(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                arg_dict = _get_args(signature, args, kwargs)
                logger.error(str(e), extra={"extra": {"function_name": func.__name__, "args": arg_dict}})
                if handle_error:
                    return None
                else:
                    raise e

        return wrapper
    return decorator