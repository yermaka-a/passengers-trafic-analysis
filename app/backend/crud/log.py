from ..schemas import LogRequest

from ..logger import log


class LogsController:

    def __init__(self) -> None:
        pass

    def write_log(self, data):
        try:
            logs = LogRequest(**data)
            log.info(
                "frontend",
                level=logs.level,
                msg=logs.msg,
                extra=logs.extra_info,
            )

        except Exception as e:
            op = "write_log"
            log.error(f"{op}: incorrect log", error=e)
