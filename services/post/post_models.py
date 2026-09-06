from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class Owner(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    firstName: str = Field(min_length=2, max_length=50)
    lastName: str = Field(min_length=2, max_length=50)


class PostPreviewResponseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    image: str
    likes: int = Field(strict=True, ge=0)
    tags: list[str]
    text: str
    publishDate: datetime
    updatedDate: datetime
    owner: Owner


class PostResponseModel(PostPreviewResponseModel):
    """Full post contract used for create/get/update responses."""

    image: str = Field(min_length=1)
    link: str | None = None
    text: str = Field(min_length=6, max_length=1000)


class PostListResponseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")

    # DummyAPI's public seed data contains legacy empty images and very short text.
    # Keep metadata and types strict without applying create-time constraints here.
    data: list[PostPreviewResponseModel]
    total: int = Field(strict=True, ge=0)
    page: int = Field(strict=True, ge=0, le=999)
    limit: int = Field(strict=True, ge=5, le=50)


class PostDeleteResultModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
