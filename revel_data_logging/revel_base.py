import logging
from abc import ABC, abstractmethod
from typing import Any


class RevelBaseFormatter(logging.Formatter, ABC):
    _params: {}

    @abstractmethod
    def add_param(self, name: str, default: Any = None):
        pass