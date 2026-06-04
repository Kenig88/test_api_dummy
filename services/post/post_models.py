from datetime import datetime

from pydantic import BaseModel, ConfigDict


class Owner(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    firstName: str
    lastName: str


class PostResponseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    image: str
    likes: int
    link: str | None = None
    tags: list[str]
    text: str
    publishDate: datetime
    updatedDate: datetime
    owner: Owner


class PostListResponseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")

    data: list[PostResponseModel]
    total: int
    page: int
    limit: int


class PostDeleteResponseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str


class PostAfterDeleteResponseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    error: str
