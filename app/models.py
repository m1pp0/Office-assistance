import enum
from datetime import datetime, timezone
from sqlalchemy import (Column, Integer, String, ForeignKey, Date, DateTime, Enum as SQLEnum, UniqueConstraint)
from sqlalchemy.orm import relationship
from app.database import Base

class ResourceType(str, enum.Enum):
    DESK = "desk"
    ROOM = "room"


class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

    users = relationship("User", back_populates="team")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)

    team = relationship("Team", back_populates="users")
    bookings = relationship("Booking", back_populates="user")


class Desk(Base):
    __tablename__ = "desks"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False)
    zone = Column(String(50), nullable=False)


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    capacity = Column(Integer, default=4, nullable=False)


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    resource_type = Column(SQLEnum(ResourceType), nullable=False)
    resource_id = Column(Integer, nullable=False)
    
    booking_date = Column(Date, nullable=False, index=True)
    status = Column(SQLEnum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    
    created_at = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        nullable=False
    )

    user = relationship("User", back_populates="bookings")

    __table_args__ = (
        UniqueConstraint(
            "resource_type", 
            "resource_id", 
            "booking_date",
        ),
    )