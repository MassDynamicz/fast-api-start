from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class RoleBase(BaseModel):
    name: str
    description: str

class RoleCreate(RoleBase):
    pass

class Role(RoleBase):
    id: int

    class Config:
        from_attributes = True

class UserSessionBase(BaseModel):
    session_start: datetime
    session_end: Optional[datetime]
    data_used: int
    description: str

class UserSession(UserSessionBase):
    id: int

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    phone: str
    address: str
    company: str
    is_active: bool

class UserCreate(UserBase):
    password: str
    roles: List[int]

class User(UserBase):
    id: int
    last_login_at: datetime
    is_admin: bool
    roles: List[Role] = []
    sessions: List[UserSession] = []

    class Config:
        from_attributes = True

    @staticmethod
    def from_orm(user):
        user_dict = user.__dict__
        return User(**user_dict)
