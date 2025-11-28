import logging
import sys
import os


class REVELLogger(logging.Logger):
    _current_loggers: list[logging.Logger] = []
    """REVEL-aware logger with structured context and helper behavior.

        This logger extends :class:`logging.Logger` to make it easy to work
        with REVEL formatters:

          * It accepts keyword arguments in the constructor that are stored as
            logger-level context and injected into every log record.
          * It overrides the standard logging methods (``info``, ``warning``,
            ``error``, ``debug``, ``critical``) to pass a nested ``extra`` dict
            that REVEL formatters know how to consume.
          * It can be used as a context manager to automatically log success or
            failure messages when a code block finishes.

        The logger is typically configured with a REVEL JSON formatter so that
        all structured context ends up in the final JSON log line.
    """
    _success_bkp = None
    _fail_bkp = None
    _stdout_bkp = None
    _stderr_bkp = None
    _context_params_name = None
    _context_params = {}

    @classmethod
    def set_level(cls, level: str | int):
        for logger in cls._current_loggers:
            logger.setLevel(level)

    def __init__(
            self,
            name,
            *handlers,
            success_msg="success",
            exc_msg="failed",
            handle_error=False,
            level=0,
            outer_logs_disabled=False,
            stdout = None,
            stderr = None,
            **extra
    ):
        """Create a REVELLogger.

                Args:
                    name: Logger name.
                    *handlers: Optional logging handlers to attach to this logger.
                    success_msg: Default message used when the logger is used as a
                        context manager and the block finishes without raising.
                    exc_msg: Default message used when the logger is used as a
                        context manager and the block exits with an exception.
                    handle_error: If ``True``, exceptions raised inside a context
                        manager block are logged and swallowed; if ``False``, the
                        exception is re-raised after logging.
                    level: Initial logging level for the logger.
                    **extra: Arbitrary context that should be attached to every
                        record emitted by this logger. The context is added under
                        the logger's name inside the ``extra`` dict.
        """
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

        self._outer_logs_disabled = outer_logs_disabled
        self._parse_stdio(stdout, stderr)

        REVELLogger._current_loggers.append(self)

    @property
    def extra(self):
        return self._extra

    def __del__(self):
        REVELLogger._current_loggers.remove(self)
        del self

    def __enter__(self):
        if self._outer_logs_disabled:
            self._stdout_bkp = sys.stdout
            self._stderr_bkp = sys.stderr
            sys.stdout = self._stdout
            sys.stderr = self._stderr

        if self._context_params_name:
            self._extra[self._context_params_name] = self._context_params

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

        if self._outer_logs_disabled:
            sys.stdout = self._stdout_bkp
            sys.stderr = self._stderr_bkp
            self._stdout_bkp = None
            self._stderr_bkp = None

        if self._context_params_name:
            self._extra.pop(self._context_params_name, None)
            self._context_params_name = None
            self._context_params = None

        if exc_type is None:
            self.info(success)
        else:

            exc_info = {
                "error_type": exc_type.__name__,
                "error_value": exc_val
            }

            if self._handle_error:
                self.warning(fail, exc=exc_info)
            else:
                self.error(fail, exc=exc_info)
        return self._handle_error

    def __setitem__(self, key, value):
        self.add_param(key, value)

    def add_param(self, param, value):
        if self._extra:
            self._extra[param] = value
        else:
            self._extra = {param: value}

    def _parse_stdio(self, stdout, stderr):
        if stdout is None:
            stdout = open(os.devnull, "w")
        if stderr is None:
            stderr = open(os.devnull, "w")

        self._stdout = stdout
        self._stderr = stderr

    def with_message(self, success, fail=None):
        """
        This helper is intended for use with the context manager protocol.
        It temporarily overrides the success and failure messages used by
        :meth:`__exit__` for the next ``with`` block.

        Args:
            success: Message to log when the block exits successfully.
            fail: Optional message to log when the block fails with an
                exception. If ``None``, the logger's default failure
                message is used.
        :param success:
        :param fail:
        :return:
        """
        self._success_bkp = success
        self._fail_bkp = fail
        return self

    def disable_outer_logs(self, stdout = None, stderr = None):
        self._outer_logs_disabled = True
        self._parse_stdio(stdout, stderr)
        return self

    def with_context_params(self, name, **params):
        self._context_params_name = name
        self._context_params = params
        return self

    def info(
            self,
            msg,
            *args,
            exc_info=None,
            stack_info=False,
            stacklevel=1,
            **extra
    ):
        if isinstance(extra, dict):
            extra[self.name] = self._extra
        super().info(msg, *args, exc_info=exc_info, stack_info=stack_info, stacklevel=stacklevel,
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
        if isinstance(extra, dict):
            extra[self.name] = self._extra
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
        if isinstance(extra, dict):
            extra[self.name] = self._extra
        super().error(msg, *args, exc_info=exc_info, stack_info=stack_info, stacklevel=stacklevel,
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
        if isinstance(extra, dict):
            extra[self.name] = self._extra
        super().debug(msg, *args, exc_info=exc_info, stack_info=stack_info, stacklevel=stacklevel,
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
        if isinstance(extra, dict):
            extra[self.name] = self._extra
        super().critical(msg, *args, exc_info=exc_info, stack_info=stack_info, stacklevel=stacklevel,
                         extra={"extra": extra})
