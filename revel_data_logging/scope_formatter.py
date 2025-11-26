import logging

from revel_data_logging.interfaces import _RevelFormatter


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
        for _handler in logger.handlers:
            if isinstance(_handler.formatter, _RevelFormatter):
                _handler.formatter.add_param(name)

        self._name = name
        super().__init__(logger, extra)

    def process(self, msg, kwargs):
        extra = kwargs.get("extra", {}).get("extra", {})
        extra[self._name] = self.extra
        return f"{msg}", {"extra": {"extra": extra}}