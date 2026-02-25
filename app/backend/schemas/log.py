from typing import Optional

from pydantic import BaseModel, Field


class LogRequest(BaseModel):
    msg: str
    level: str
    extra_info: Optional[dict] | None = Field(
        None,
        alias="extraInfo",
        serialization_alias="extraInfo",
    )
