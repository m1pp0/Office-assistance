from datetime import date
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Room, Booking, ResourceType, BookingStatus
from app.schemas import RoomResponse, RoomStateResponse

router = APIRouter(prefix="/rooms", tags=["Переговорные комнаты"])


@router.get("", response_model=List[RoomResponse])
def get_all_rooms(db: Session = Depends(get_db)):
    return db.query(Room).all()


@router.get("/state", response_model=List[RoomStateResponse])
def get_rooms_state(
    booking_date: date = Query(default_factory=date.today, description="Дата бронирования"),
    db: Session = Depends(get_db)
):
    rooms = db.query(Room).all()

    bookings = db.query(Booking).filter(
        Booking.resource_type == ResourceType.ROOM,
        Booking.booking_date == booking_date,
        Booking.status != BookingStatus.CANCELLED
    ).all()

    bookings_map = {b.resource_id: b for b in bookings}

    result = []
    for room in rooms:
        booking = bookings_map.get(room.id)
        is_booked = booking is not None

        result.append(RoomStateResponse(
            id=room.id,
            name=room.name,
            capacity=room.capacity,
            is_booked=is_booked,
            booking_id=booking.id if is_booked else None,
            booked_by_user_id=booking.user_id if is_booked else None,  # <-- ДОБАВИТЬ ЭТУ СТРОКУ
            status=booking.status if is_booked else None,
            booked_by_name=booking.user.full_name if (is_booked and booking.user) else None
        ))

    return result