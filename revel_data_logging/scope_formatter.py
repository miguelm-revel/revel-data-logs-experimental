import logging

from .interfaces import _RevelFormatter
from .revel_logger import REVELLogger


class ContextLogger(logging.LoggerAdapter):
    """Logger adapter that injects fixed contextual information.

        A ``ContextLogger`` wraps an existing logger and adds a constant value
        under a given key to every log record emitted through it. It also
        registers that key in any REVEL formatter attached to the underlying
        logger so that the field is always present in the formatted output.

        This is useful for attaching high-level context such as ``request_id``,
        ``user_id`` or ``job_id`` to all logs produced within a scope.
    """

    def __init__(self, logger, name, extra=None):
        """Create a new contextual logger.

                Args:
                    logger: Base logger or :class:`REVELLogger` instance that will
                        actually emit the records.
                    name: Name of the context field to inject (for example
                        ``"request_id"``).
                    extra: Value to associate with the context field for this
                        adapter. This value is added to the structured ``extra``
                        dict on every log call.
        """
        has_revel_formatter = False
        for _handler in logger.handlers:
            if isinstance(_handler.formatter, _RevelFormatter):
                has_revel_formatter = True
                break
        assert has_revel_formatter, "logger must have at least one revel formatter"

        self._name = name
        super().__init__(logger, extra)

    def process(self, msg, kwargs):
        existing = kwargs.get("extra", {}).get("extra", {})
        merged = {**existing, self._name: self.extra}
        if isinstance(self.logger, REVELLogger):
            merged[self.logger.name] = self.logger.extra
        return msg, {"extra": {"extra": merged}}

    def info(
            self,
            msg,
            *args,
            exc_info=None,
            stack_info=False,
            stacklevel=1,
            **extra
    ):
        super().info(msg, *args, exc_info=exc_info, stack_info=stack_info, stacklevel=stacklevel,
                     extra={"extra": extra})

    def debug(
            self,
            msg,
            *args,
            exc_info=None,
            stack_info=False,
            stacklevel=1,
            **extra
    ):
        super().debug(msg, *args, exc_info=exc_info, stack_info=stack_info, stacklevel=stacklevel,
                      extra={"extra": extra})

    def warning(
            self,
            msg,
            *args,
            exc_info=None,
            stack_info=False,
            stacklevel=1,
            **extra
    ):
        super().warning(msg, *args, exc_info=exc_info, stack_info=stack_info, stacklevel=stacklevel,
                        extra={"extra": extra})

    def error(
            self,
            msg,
            *args,
            exc_info=None,
            stack_info=False,
            stacklevel=1,
            **extra
    ):
        super().error(msg, *args, exc_info=exc_info, stack_info=stack_info, stacklevel=stacklevel,
                      extra={"extra": extra})

    def critical(
            self,
            msg,
            *args,
            exc_info=None,
            stack_info=False,
            stacklevel=1,
            **extra
    ):
        super().critical(msg, *args, exc_info=exc_info, stack_info=stack_info, stacklevel=stacklevel,
                         extra={"extra": extra})
