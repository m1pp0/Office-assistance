from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict
from app.models import ResourceType, BookingStatus


class TeamBase(BaseModel):
    name: str

# class TeamCreate(TeamBase):
#     pass

class TeamResponse(TeamBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    team_id: Optional[int] = None

# class UserCreate(UserBase):
#     password: str

class UserResponse(UserBase):
    id: int
    team: Optional[TeamResponse] = None
    model_config = ConfigDict(from_attributes=True)


class DeskResponse(BaseModel):
    id: int
    code: str
    zone: str
    model_config = ConfigDict(from_attributes=True)

class RoomResponse(BaseModel):
    id: int
    name: str
    capacity: int
    model_config = ConfigDict(from_attributes=True)


class BookingCreate(BaseModel):
    resource_type: ResourceType
    resource_id: int
    booking_date: date

class BookingResponse(BaseModel):
    id: int
    user_id: int
    resource_type: ResourceType
    resource_id: int
    booking_date: date
    status: BookingStatus
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class DeskStateResponse(BaseModel):
    id: int
    code: str
    zone: str
    is_booked: bool
    booked_by_name: Optional[str] = None
    booked_by_user_id: Optional[int] = None
    booking_id: Optional[int] = None
    is_teammate: bool = False

class RoomStateResponse(BaseModel):
    id: int
    name: str
    capacity: int
    is_booked: bool
    booking_id: Optional[int] = None
    booked_by_user_id: Optional[int] = None 
    status: Optional[BookingStatus] = None
    booked_by_name: Optional[str] = None

class OfficeStateResponse(BaseModel):
    date: date
    desks: List[DeskStateResponse]
    rooms: List[RoomStateResponse]


# class Token(BaseModel):
#     access_token: str
#     token_type: str = "bearer"

# class TokenData(BaseModel):
#     email: Optional[str] = None