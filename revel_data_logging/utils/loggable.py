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