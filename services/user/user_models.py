from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, EmailStr


# Для create, get user by id, update user
class UserResponseModel(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    firstName: str = Field(min_length=2, max_length=50)
    lastName: str = Field(min_length=2, max_length=50)
    email: EmailStr
    dateOfBirth: datetime
    phone: str
    registerDate: datetime
    updatedDate: datetime


class UserList(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    title: Optional[str] | None = None
    firstName: str = Field(min_length=2, max_length=50)
    lastName: str = Field(min_length=2, max_length=50)
    picture: Optional[str] | None = None


# для get_list_users()
class UserListResponseModel(BaseModel):
    model_config = ConfigDict(extra="allow")

    data: List[UserList]
    total: int
    page: int
    limit: int


class UserDeleteResponseModel(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str


class UserAfterDeleteResponseModel(BaseModel):
    error: str
