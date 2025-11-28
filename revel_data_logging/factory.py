import logging
import sys
from typing import Literal

from .json_formatter import JSONFormatter
from .revel_logger import REVELLogger
from .pretty_console import PrettyConsoleFormatter

def get_logger(logger_name: str, env:Literal["pro", "dev"] = "pro", formatter_params=None, **logger_params) -> REVELLogger:
    """
        Create and configure a REVEL logger using the appropriate formatter
        depending on the execution environment.

        This function acts as a factory that returns a fully configured
        :class:`REVELLogger` instance with a single stdout handler and one of the
        standard REVEL formatters:

          - ``JSONFormatter`` when ``env="pro"`` (production environments).
          - ``PrettyConsoleFormatter`` when ``env="dev"`` (development/local environments).

        It ensures consistent, standardized logging across all services without
        requiring each service to manage its own logging configuration.

        Parameters
        ----------
        logger_name : str
            Name of the logger, typically the module or service name.
        env : Literal["pro", "dev"]
            Execution environment. Determines which formatter is used:
            - ``"pro"`` → structured JSON logs suitable for observability pipelines.
            - ``"dev"`` → human-friendly, colored console output.
        formatter_params : dict, optional
            Additional parameters passed directly to the selected formatter
            (e.g., ``service="checkout"``, ``env="local"``, etc.).
            Defaults to an empty dictionary.
        **logger_params : Any
            Additional keyword arguments forwarded to the :class:`REVELLogger`
            constructor. Useful for setting default context values, log levels,
            or service metadata.

        Returns
        -------
        REVELLogger
            A fully configured logger instance ready for use.

        Raises
        ------
        AssertionError
            If ``env`` is not ``"pro"`` or ``"dev"``.

        Examples
        --------
        >>> logger = get_logger("checkout.api", env="dev", service="checkout")
        >>> logger.info("Payment completed", order_id="ABC-123")

        >>> prod_logger = get_logger(
        ...     "billing.worker",
        ...     env="pro",
        ...     formatter_params={"service": "billing"},
        ... )
        >>> prod_logger.error("Failed to process invoice", invoice_id=987)
        """
    assert env in ["pro", "dev"], "env must be pro or dev"
    if formatter_params is None:
        formatter_params = {}
    if env == "pro":
        formatter = JSONFormatter(**formatter_params)
    else:
        formatter = PrettyConsoleFormatter(**formatter_params)
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)
    logger = REVELLogger(logger_name, handler, **logger_params)
    return logger