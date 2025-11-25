
import json
import logging
from typing import Any

from .revel_base import RevelBaseFormatter
from .serde import json_serialize

class JSONFormatter(RevelBaseFormatter):
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
