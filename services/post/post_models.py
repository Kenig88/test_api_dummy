from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


class Owner(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    firstName: str
    lastName: str


# для create, get_post_by_post_id, update
class PostResponseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    image: str
    likes: int
    link: Optional[str] | None = None
    tags: List[str]
    text: str
    publishDate: datetime
    updatedDate: datetime
    owner: Owner


# для get_list_posts, get_list_posts_by_user_id
class PostListResponseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")

    data: List[PostResponseModel]
    total: int
    page: int
    limit: int


# для delete
class PostDeleteResponseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str


class PostAfterDeleteResponseModel(BaseModel):
    model_config = ConfigDict(extra="allow")

    error: str
