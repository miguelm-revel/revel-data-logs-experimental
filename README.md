# Revel Data Logging 

````python
import logging
from revel_data_logging import JSONFormatter, REVELLogger, ContextLogger
from revel_data_logging.utils import loggable, error_logs

# ---------------------------------------------------------------------------
# Configuración base
# ---------------------------------------------------------------------------

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())

base_logger = REVELLogger(
    "payments",
    handler,
    success_msg="payments block finished",  # OPT
    exc_msg="payments block failed",        # OPT
    handle_error=True,                      # OPT captura excepciones en context manager
    # contexto fijo del logger
    service="payments",
    env="prod",
)

base_logger.setLevel(logging.INFO)

# ---------------------------------------------------------------------------
# Logs básicos
# ---------------------------------------------------------------------------

base_logger.info("payment created", order_id="ORD-123", amount=10.5)
# {
#   "level": "INFO",
#   "time": "2025-11-27 11:34:40,868",
#   "message": "payment created",
#   "order_id": "ORD-123",
#   "amount": 10.5,
#   "payments": {
#     "service": "payments",
#     "env": "prod"
#   }
# }

base_logger.error("payment failed", order_id="ORD-456", reason="insufficient_funds")
# {
#   "level": "ERROR",
#   "time": "2025-11-27 11:34:40,869",
#   "message": "payment failed",
#   "order_id": "ORD-456",
#   "reason": "insufficient_funds",
#   "payments": {
#     "service": "payments",
#     "env": "prod"
#   }
# }

# ---------------------------------------------------------------------------
# Context manager (éxito / fallo)
# ---------------------------------------------------------------------------

with base_logger.with_message(success="user created", fail="user creation failed"):
    ...
# {
#   "level": "INFO",
#   "time": "2025-11-27 11:34:40,869",
#   "message": "user created",
#   "payments": {
#     "service": "payments",
#     "env": "prod"
#   }
# }

with base_logger.with_message(success="user created", fail="user creation failed"):
    1 / 0
# {
#   "level": "WARNING",
#   "time": "2025-11-27 11:34:40,869",
#   "message": "user creation failed",
#   "exc": {
#     "error_type": "ZeroDivisionError",
#     "error_value": "division by zero"
#   },
#   "payments": {
#     "service": "payments",
#     "env": "prod"
#   }
# }

# ---------------------------------------------------------------------------
# Logger derivados con un scope (ContextLogger)
# ---------------------------------------------------------------------------

def handle_request(request_id: str):
    logger = ContextLogger(base_logger, "request_id", extra=request_id)

    logger.info("starting request")
    # {
    #   "level": "INFO",
    #   "time": "2025-11-27 11:34:40,869",
    #   "message": "starting request",
    #   "request_id": "abc123",
    #   "payments": {
    #     "service": "payments",
    #     "env": "prod"
    #   }
    # }

    ...
    logger.info("finishing request")
    # {
    #   "level": "INFO",
    #   "time": "2025-11-27 11:34:40,869",
    #   "message": "finishing request",
    #   "request_id": "abc123",
    #   "payments": {
    #     "service": "payments",
    #     "env": "prod"
    #   }
    # }


handle_request("abc123")

# ---------------------------------------------------------------------------
# Decoradores: loggable y error_logs
# ---------------------------------------------------------------------------

@loggable(base_logger)
def user_login(user_id: str, method: str = "password"):
    ...
    return True


user_login("abc123")
# {
#   "level": "INFO",
#   "time": "2025-11-27 11:34:40,869",
#   "message": "func user_login called",
#   "args": {
#     "user_id": "abc123",
#     "method": "password"
#   },
#   "payments": {
#     "service": "payments",
#     "env": "prod"
#   }
# }


@error_logs(base_logger, handle_error=True)
def process_job(job_id: str, retries: int):
    1 / 0


process_job("123456", 4)
# {
#   "level": "ERROR",
#   "time": "2025-11-27 11:34:40,869",
#   "message": "division by zero",
#   "function_name": "process_job",
#   "args": {
#     "job_id": "123456",
#     "retries": 4
#   },
#   "payments": {
#     "service": "payments",
#     "env": "prod"
#   }
# }

# ---------------------------------------------------------------------------
# NUEVAS FUNCIONALIDADES DEL REVELLogger
# ---------------------------------------------------------------------------

# 1) Cambiar el nivel de *todos* los REVELLogger activos

REVELLogger.set_level(logging.DEBUG)
base_logger.debug("this debug will now be visible")

# 2) Añadir campos de contexto dinámicamente (como si fuera un dict)

base_logger["region"] = "eu-west-1"
base_logger["service_group"] = "billing"

base_logger.info("log with extra context", operation="reconcile")
# → el JSON incluirá:
#   "payments": {
#     "service": "payments",
#     "env": "prod",
#     "region": "eu-west-1",
#     "service_group": "billing"
#   }

# 3) with_context_params: meter un sub-dict temporal bajo una clave

with base_logger.with_context_params(
    "context",
    operation="refresh_balances",
    correlation_id="corr-123",
):
    base_logger.info("running refresh operation")
# → dentro del with:
#     "payments": {
#       "service": "payments",
#       "env": "prod",
#       "region": "eu-west-1",
#       "service_group": "billing",
#       "context": {
#         "operation": "refresh_balances",
#         "correlation_id": "corr-123"
#       }
#     }
#   Fuera del with, la clave "context" se elimina del extra del logger.

# 4) disable_outer_logs: silenciar prints de dentro del bloque

with base_logger.disable_outer_logs():
    print("esto no se verá en stdout real")
    base_logger.info("inside block with outer logs disabled")
# → los logs siguen saliendo por el handler, pero stdout/stderr
#   dentro del with van a /dev/null (a menos que pases streams propios).

# 5) Combinar disable_outer_logs + with_message en un mismo contexto

with base_logger.disable_outer_logs().with_message(
    success="batch finished",
    fail="batch failed",
):
    # prints silenciosos, logs JSON normales
    print("preparing batch")
    ...
    # si algo lanza excepción aquí dentro:
    # - se loggea WARNING/ERROR con "batch failed"
    # - stdout/stderr se restauran al salir
    # - si handle_error=True, no se propaga la excepción
    raise RuntimeError("something bad happened")

````