import logging
from typing import Any, Dict, Mapping, Sequence

from .revel_base import RevelBaseFormatter


class PrettyConsoleFormatter(RevelBaseFormatter):
    """Formatter que pinta los logs de forma legible y coloreada en consola.

    - Incluye: timestamp, nivel, logger.name (opcional) y mensaje.
    - Acepta parámetros por defecto en el constructor (service, env, etc.).
    - Mezcla esos parámetros con record.extra (rellenado por loggers REVEL).
    - El contexto se muestra en bloque aparte, con soporte multinivel para dicts/listas.
    """

    _RESET = "\x1b[0m"
    _BOLD = "\x1b[1m"
    _DIM = "\x1b[2m"

    _FG_COLORS = {
        "grey": "\x1b[90m",
        "red": "\x1b[31m",
        "green": "\x1b[32m",
        "yellow": "\x1b[33m",
        "blue": "\x1b[34m",
        "magenta": "\x1b[35m",
        "cyan": "\x1b[36m",
        "white": "\x1b[37m",
    }

    _LEVEL_COLORS = {
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "red",
    }

    def __init__(
        self,
        use_color: bool = True,
        show_logger_name: bool = True,
        context_indent: int = 4,
        **params: Any,
    ) -> None:
        """Crea un PrettyConsoleFormatter.

        Args:
            use_color: Si False, desactiva todos los códigos ANSI.
            show_logger_name: Si True, muestra record.name.
            context_indent: Número de espacios de indentación para el bloque de contexto.
            **params: Parámetros por defecto a incluir en el contexto (service, env, etc.).
        """
        self._params: Dict[str, Any] = params
        self._use_color = use_color
        self._show_logger_name = show_logger_name
        self._context_indent = context_indent
        super().__init__()

    def add_param(self, name: str, default: Any = None) -> None:
        self._params[name] = default

    # === Helpers de estilo / color ===

    def _color(self, text: str, *, fg: str | None = None, bold: bool = False, dim: bool = False) -> str:
        if not self._use_color:
            return text

        codes = []
        if bold:
            codes.append(self._BOLD)
        if dim:
            codes.append(self._DIM)
        if fg is not None and fg in self._FG_COLORS:
            codes.append(self._FG_COLORS[fg])

        if not codes:
            return text

        return "".join(codes) + text + self._RESET

    def _style_level(self, levelname: str) -> str:
        color = self._LEVEL_COLORS.get(levelname, "white")
        bold = levelname in ("WARNING", "ERROR", "CRITICAL")
        return self._color(levelname, fg=color, bold=bold)

    def _style_time(self, ts: str) -> str:
        return self._color(ts, fg="grey", dim=True)

    def _style_logger_name(self, name: str) -> str:
        return self._color(name, fg="blue", dim=True)

    def _style_key(self, key: str) -> str:
        return self._color(key, fg="grey", bold=True)

    # === Construcción de contexto ===

    def _build_context(self, record: logging.LogRecord) -> Dict[str, Any]:
        context: Dict[str, Any] = dict(self._params)
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            context.update(record.extra)
        return context

    # === Formateo del mensaje principal ===

    def _format_message_block(self, header: str, message: str) -> str:
        if "\n" not in message:
            return f"{header} {message}"

        lines = message.splitlines()
        first = lines[0]
        rest = lines[1:]

        # Un prefijo visual para las líneas siguientes
        continuation_prefix = " " * len(header) + " "
        if self._use_color:
            continuation_prefix += self._color("│ ", fg="grey", dim=True)
        else:
            continuation_prefix += "│ "

        formatted_rest = "\n".join(continuation_prefix + line for line in rest)
        return f"{header} {first}\n{formatted_rest}"

    # === Formateo multinivel del contexto ===

    @staticmethod
    def _is_scalar(value: Any) -> bool:
        return isinstance(value, (str, int, float, bool)) or value is None

    def _format_complex_value(self, value: Any, base_indent: str, level: int) -> str:
        """Formatea dicts/listas/tuplas en varias líneas con indentación."""
        indent = base_indent + "  " * level
        lines: list[str] = []

        if isinstance(value, Mapping):
            for k, v in value.items():
                styled_key = self._style_key(str(k))
                if self._is_scalar(v):
                    lines.append(f"{indent}{styled_key}={v!r}")
                else:
                    lines.append(f"{indent}{styled_key}:")
                    lines.append(self._format_complex_value(v, base_indent, level + 1))
        elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            for idx, item in enumerate(value):
                prefix = f"[{idx}]"
                styled_key = self._style_key(prefix)
                if self._is_scalar(item):
                    lines.append(f"{indent}{styled_key}={item!r}")
                else:
                    lines.append(f"{indent}{styled_key}:")
                    lines.append(self._format_complex_value(item, base_indent, level + 1))
        else:
            # fallback por si llega algo raro
            lines.append(f"{indent}{value!r}")

        return "\n".join(lines)

    def _format_context_block(self, context: Dict[str, Any]) -> str:
        if not context:
            return ""

        base_indent = " " * self._context_indent
        bullet = "└─"
        if self._use_color:
            bullet = self._color(bullet, fg="grey", dim=True)

        # Separamos en escalares y complejos para que lo sencillo quede en una línea
        scalars: Dict[str, Any] = {}
        complex_items: Dict[str, Any] = {}

        for key, value in context.items():
            if self._is_scalar(value):
                scalars[key] = value
            else:
                complex_items[key] = value

        lines: list[str] = []

        # Línea principal con escalares (env, service, order_id, amount, etc.)
        if scalars:
            parts = []
            for key in sorted(scalars.keys()):
                styled_key = self._style_key(key)
                parts.append(f"{styled_key}={scalars[key]!r}")
            lines.append(f"{base_indent}{bullet} " + " ".join(parts))
        else:
            # Si no hay escalares pero sí complejos, seguimos usando la bala
            lines.append(f"{base_indent}{bullet}")

        # Bloques adicionales para los valores complejos (dicts/listas)
        for key in sorted(complex_items.keys()):
            styled_key = self._style_key(key)
            lines.append(f"{base_indent}   {styled_key}:")
            lines.append(self._format_complex_value(complex_items[key], base_indent, level=2))

        return "\n" + "\n".join(lines)

    # === API principal ===

    def format(self, record: logging.LogRecord) -> str:
        record.message = record.getMessage()
        timestamp = self.formatTime(record, self.datefmt)

        context = self._build_context(record)

        parts = [
            self._style_time(timestamp),
            f"[{self._style_level(record.levelname)}]",
        ]

        if self._show_logger_name:
            parts.append(self._style_logger_name(record.name) + ":")

        header = " ".join(parts)

        formatted = self._format_message_block(header, record.message)
        formatted += self._format_context_block(context)

        return formatted
