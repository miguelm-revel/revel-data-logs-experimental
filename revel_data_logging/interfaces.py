from typing import Protocol, runtime_checkable, Any


@runtime_checkable
class _RevelFormatter(Protocol):
    _params: dict

    def add_param(self, name: str, default: Any = None):
        pass
