import logging
from copy import copy


class REVELLogger(logging.Logger):

    def __init__(self, name, *handlers, success_msg="success", exc_msg="failed", handle_error = False, level = 0, **extra):
        if extra:
            self._extra = {"extra": extra}
        else:
            self._extra = None
        self._success_msg = success_msg
        self._exc_msg = exc_msg
        self._handle_error = handle_error
        super().__init__(name, level)
        if handlers:
            for handler in handlers:
                self.addHandler(handler)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.info(self._success_msg, extra = self._extra)
        else:
            extra = copy(self._extra)
            extra["error_type"] = exc_type.__name__
            extra["error_value"] = exc_val

            if self._handle_error:
                self.warning(self._exc_msg, extra=extra)
            else:
                self.error(self._exc_msg, extra=extra)
        return self._handle_error

    def info(
        self,
        msg,
        *args,
        exc_info = None,
        stack_info = False,
        stacklevel = 1,
        **extra
    ):
        super().info(msg, *args, exc_info=exc_info, stack_info=stack_info, stacklevel=stacklevel, extra={"extra": extra})

    def warning(
        self,
        msg,
        *args,
        exc_info = None,
        stack_info = False,
        stacklevel = 1,
        **extra
    ):
        super().warning(msg, *args, exc_info=exc_info, stack_info=stack_info, stacklevel=stacklevel, extra={"extra": extra})

    def error(
        self,
        msg,
        *args,
        exc_info = None,
        stack_info = False,
        stacklevel = 1,
        **extra
    ):
        super().error(msg, *args, exc_info=exc_info, stack_info=stack_info, stacklevel=stacklevel, extra={"extra": extra})

    def debug(
        self,
        msg,
        *args,
        exc_info = None,
        stack_info = False,
        stacklevel = 1,
        **extra
    ):
        super().debug(msg, *args, exc_info=exc_info, stack_info=stack_info, stacklevel=stacklevel, extra={"extra": extra})

    def critical(
        self,
        msg,
        *args,
        exc_info = None,
        stack_info = False,
        stacklevel = 1,
        **extra
    ):
        super().critical(msg, *args, exc_info=exc_info, stack_info=stack_info, stacklevel=stacklevel, extra={"extra": extra})