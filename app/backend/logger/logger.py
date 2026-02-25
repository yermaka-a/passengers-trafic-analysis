import logging
import structlog
import sys

from structlog.stdlib import BoundLogger

from ..config import LogConfig

# 1. Общие процессоры (подготовка данных)
shared_processors = [
    structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
    structlog.stdlib.add_log_level,
    structlog.stdlib.add_logger_name,
    structlog.processors.format_exc_info,
    structlog.processors.StackInfoRenderer(),
    structlog.stdlib.PositionalArgumentsFormatter(),
    structlog.processors.UnicodeDecoder(),
]

# 2. Конфигурация structlog
structlog.configure(
    processors=shared_processors
    + [
        # Это связывает structlog со стандартным logging
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# 3. Настройка форматтеров (обработка того, ЧТО пришло из лога)
# ВАЖНО: добавляем foreign_pre_chain, чтобы данные не терялись
file_formatter = structlog.stdlib.ProcessorFormatter(
    processor=structlog.processors.JSONRenderer(),
    foreign_pre_chain=shared_processors,
)

console_formatter = structlog.stdlib.ProcessorFormatter(
    processor=structlog.dev.ConsoleRenderer(colors=True),
    foreign_pre_chain=shared_processors,
)

file_handler = logging.FileHandler(LogConfig.LOG_FILE_PATH)
file_handler.setFormatter(file_formatter)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(console_formatter)

logger = logging.getLogger("app_logger")
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

log: BoundLogger = structlog.wrap_logger(logger)
