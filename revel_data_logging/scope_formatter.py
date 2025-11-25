import logging

from revel_data_logging.interfaces import _RevelFormatter


class ContextLogger(logging.LoggerAdapter):
    def __init__(self, logger, name, extra=None):
        for _handler in logger.handlers:
            if isinstance(_handler.formatter, _RevelFormatter):
                _handler.formatter.add_param(name)

        self._name = name
        super().__init__(logger, extra)

    def process(self, msg, kwargs):
        extra = kwargs.get("extra", {}).get("extra", {})
        extra[self._name] = self.extra
        return f"{msg}", {"extra": {"extra": extra}}