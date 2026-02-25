import logging
from ..config import LogConfig


logger = logging.getLogger("logger")
file_handler = logging.FileHandler(LogConfig.LOG_FILE_PATH)
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s : %(levelname)s : %(name)s : %(message)s")
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

logger.addHandler(file_handler)
logger.addHandler(console_handler)
