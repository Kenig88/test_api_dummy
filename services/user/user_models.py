from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserResponseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    firstName: str = Field(min_length=2, max_length=50)
    lastName: str = Field(min_length=2, max_length=50)
    email: EmailStr
    dateOfBirth: datetime
    phone: str = Field(min_length=1)
    registerDate: datetime
    updatedDate: datetime


class UserList(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    title: str | None = None
    firstName: str = Field(min_length=2, max_length=50)
    lastName: str = Field(min_length=2, max_length=50)
    picture: str | None = None


class UserListResponseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")

    data: list[UserList]
    total: int = Field(strict=True, ge=0)
    page: int = Field(strict=True, ge=0, le=999)
    limit: int = Field(strict=True, ge=5, le=50)


class UserDeleteResultModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
