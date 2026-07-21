from pydantic import BaseModel, ConfigDict


class ErrorResponseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    error: str
