from datetime import datetime

from pydantic import BaseModel, ConfigDict


class Owner(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    firstName: str
    lastName: str


class CommentResponseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    message: str
    owner: Owner
    post: str
    publishDate: datetime


class CommentsListResponseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")

    data: list[CommentResponseModel]
    total: int
    page: int
    limit: int


class CommentDeleteResponseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str


class CommentAfterDeleteResponseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    error: str
