import json
import logging
from typing import Any

from .revel_base import RevelBaseFormatter
from .serde import json_serialize


class JSONFormatter(RevelBaseFormatter):
    """Formatter that renders log records as a single JSON object.

        The formatter always produces a JSON string with at least the following
        keys:

          * ``level`` – the log level name.
          * ``time`` – the formatted timestamp.
          * ``message`` – the log message.

        Additional keyword arguments passed to the constructor are stored as
        default parameters and included in every record. Any values present
        in ``record.extra`` (populated by REVEL loggers) are merged on top of
        those defaults before serialization.

        Values are serialized using :func:`json.dumps` with the REVEL
        ``json_serialize`` helper as ``default`` so that datetimes and custom
        objects are handled consistently.
    """

    def __init__(self, **params):
        self._params = params

        super().__init__()

    def _parse_params(self, record: logging.LogRecord, output: dict):

        for param, default in self._params.items():
            output[param] = default

        if hasattr(record, "extra"):
            for key, value in record.extra.items():
                output[key] = value

    def add_param(self, name: str, default: Any = None):
        self._params[name] = default

    def format(self, record: logging.LogRecord):
        record.message = record.getMessage()
        timestamp = self.formatTime(record, self.datefmt)

        output = {
            "level": record.levelname,
            "time": timestamp,
            "message": record.message,
        }
        self._parse_params(record, output)
        return json.dumps(
            output,
            ensure_ascii=False,
            default=json_serialize
        )
