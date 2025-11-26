import logging
from copy import copy


class REVELLogger(logging.Logger):
    _success_bkp = None
    _fail_bkp = None

    def __init__(self, name, *handlers, success_msg="success", exc_msg="failed", handle_error = False, level = 0, **extra):
        if extra:
            self._extra = extra
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
        if self._success_bkp:
            success = self._success_bkp
        else:
            success = self._success_msg

        if self._fail_bkp:
            fail = self._fail_bkp
        else:
            fail = self._exc_msg

        self._success_bkp = None
        self._fail_bkp = None


        if exc_type is None:
            self.info(success)
        else:

            extra = {
                "extra": {
                    "error_type": exc_type.__name__,
                    "error_value": exc_val
                }
            }

            if self._handle_error:
                self.warning(fail, extra=extra)
            else:
                self.error(fail, extra=extra)
        return self._handle_error

    def with_message(self, success, fail = None):
        self._success_bkp = success
        self._fail_bkp = fail
        return self

    def info(
        self,
        msg,
        *args,
        exc_info = None,
        stack_info = False,
        stacklevel = 1,
        **extra
    ):
        if isinstance(extra, dict):
          extra[self.name] = self._extra
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
        if isinstance(extra, dict):
            extra[self.name] = self._extra
        super().warning(msg, *args, exc_info=exc_info, stack_info=stack_info, stacklevel=stacklevel,
                     extra={"extra": extra})

    def error(
        self,
        msg,
        *args,
        exc_info = None,
        stack_info = False,
        stacklevel = 1,
        **extra
    ):
        if isinstance(extra, dict):
            extra[self.name] = self._extra
        super().error(msg, *args, exc_info=exc_info, stack_info=stack_info, stacklevel=stacklevel,
                     extra={"extra": extra})

    def debug(
        self,
        msg,
        *args,
        exc_info = None,
        stack_info = False,
        stacklevel = 1,
        **extra
    ):
        if isinstance(extra, dict):
            extra[self.name] = self._extra
        super().debug(msg, *args, exc_info=exc_info, stack_info=stack_info, stacklevel=stacklevel,
                     extra={"extra": extra})

    def critical(
        self,
        msg,
        *args,
        exc_info = None,
        stack_info = False,
        stacklevel = 1,
        **extra
    ):
        if isinstance(extra, dict):
            extra[self.name] = self._extra
        super().critical(msg, *args, exc_info=exc_info, stack_info=stack_info, stacklevel=stacklevel,
                     extra={"extra": extra})