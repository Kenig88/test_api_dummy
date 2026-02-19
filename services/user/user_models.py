from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, EmailStr


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


class UserListResponseModel(BaseModel):
    id: str
    firstName: str = Field(min_length=2, max_length=50)
    lastName: str = Field(min_length=2, max_length=50)


class UserDeleteResponseModel(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
