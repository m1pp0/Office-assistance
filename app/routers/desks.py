from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Desk, Booking, User, ResourceType, BookingStatus
from app.schemas import DeskStateResponse, DeskResponse
from app.security import get_current_user

router = APIRouter(prefix="/desks", tags=["Рабочие места (Столы)"])


@router.get("", response_model=List[DeskResponse])
def get_all_desks(db: Session = Depends(get_db)):
    return db.query(Desk).all()


@router.get("/state", response_model=List[DeskStateResponse])
def get_desks_state(
    booking_date: date = Query(default_factory=date.today, description="Дата бронирования"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    desks = db.query(Desk).all()

    bookings = db.query(Booking).filter(
        Booking.resource_type == ResourceType.DESK,
        Booking.booking_date == booking_date,
        Booking.status != BookingStatus.CANCELLED
    ).all()

    bookings_map = {b.resource_id: b for b in bookings}

    result = []
    for desk in desks:
        booking = bookings_map.get(desk.id)
        is_booked = booking is not None
        
        booked_by_name = None
        is_teammate = False
        if is_booked and booking.user:
            booked_by_name = booking.user.full_name
            if current_user.team_id and booking.user.team_id == current_user.team_id:
                is_teammate = True

        result.append(DeskStateResponse(
            id=desk.id,
            code=desk.code,
            zone=desk.zone,
            is_booked=is_booked,
            booked_by_name=booked_by_name,
            booked_by_user_id=booking.user_id if is_booked else None,
            booking_id=booking.id if is_booked else None,
            is_teammate=is_teammate
        ))

    return result

