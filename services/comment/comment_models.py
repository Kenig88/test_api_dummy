from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class Owner(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    firstName: str = Field(default="", max_length=50)
    lastName: str = Field(default="", max_length=50)


class CommentResponseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    message: str = Field(default="", max_length=500)  # Убрано min_length=2
    owner: Owner
    post: str
    publishDate: datetime


class CommentsListResponseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")

    data: list[CommentResponseModel]
    total: int = Field(strict=True, ge=0)
    page: int = Field(strict=True, ge=0, le=999)
    limit: int = Field(strict=True, ge=5, le=50)


class CommentDeleteResponseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str