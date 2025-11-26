import logging
from abc import ABC, abstractmethod
from typing import Any


class RevelBaseFormatter(logging.Formatter, ABC):
    """Base class for REVEL log formatters.

        Subclasses are expected to keep a mapping of known parameters in
        ``self._params`` and implement :meth:`add_param` to register new fields
        that should appear in the formatted log output. The concrete formatter
        decides how these parameters are rendered (JSON, text, etc.).
    """
    _params: {}

    @abstractmethod
    def add_param(self, name: str, default: Any = None):
        """Register a new parameter in the formatter.

                The parameter will be available when formatting records and may be
                used to inject additional context into the final log output.

                Args:
                    name: Name of the field that may appear in the formatted log.
                    default: Default value to use for this field when the log record
                        does not provide one explicitly.
        """
        pass