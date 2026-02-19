from pydantic import BaseModel, ConfigDict
from typing import List
from datetime import datetime


class Owner(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    firstName: str
    lastName: str


# для create
class CommentResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    message: str
    owner: Owner
    post: str
    publishDate: datetime


# для get_list_by_user_id, get_list_by_post_id, get_list
class CommentList(BaseModel):
    model_config = ConfigDict(extra="ignore")

    data: List[CommentResponse]
    total: int
    page: int
    limit: int


# для delete
class CommentDeleteResponseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
