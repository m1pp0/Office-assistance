from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.models import User, Desk, Room, Booking, ResourceType, BookingStatus
from app.schemas import BookingCreate, BookingResponse
from app.security import get_current_user

router = APIRouter(prefix="/bookings", tags=["Бронирования"])


@router.post("/desk", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def book_desk(
    payload: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    desk = db.query(Desk).filter(Desk.id == payload.resource_id).first()
    if not desk:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Стол не найден")

    existing_user_booking = db.query(Booking).filter(
        Booking.user_id == current_user.id,
        Booking.resource_type == ResourceType.DESK,
        Booking.booking_date == payload.booking_date,
        Booking.status != BookingStatus.CANCELLED
    ).first()

    if existing_user_booking:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="У вас уже есть забронированный стол на эту дату"
        )

    existing_booking = db.query(Booking).filter(
        Booking.resource_type == ResourceType.DESK,
        Booking.resource_id == payload.resource_id,
        Booking.booking_date == payload.booking_date
    ).first()

    if existing_booking:
        if existing_booking.status != BookingStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Этот стол уже занят на выбранную дату"
            )
        existing_booking.user_id = current_user.id
        existing_booking.status = BookingStatus.CONFIRMED
        db.commit()
        db.refresh(existing_booking)
        return existing_booking

    new_booking = Booking(
        user_id=current_user.id,
        resource_type=ResourceType.DESK,
        resource_id=payload.resource_id,
        booking_date=payload.booking_date,
        status=BookingStatus.CONFIRMED
    )

    try:
        db.add(new_booking)
        db.commit()
        db.refresh(new_booking)
        return new_booking
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Конфликт бронирования: стол уже занят"
        )


@router.post("/room", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def book_room(
    payload: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    room = db.query(Room).filter(Room.id == payload.resource_id).first()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Переговорная не найдена")

    existing_booking = db.query(Booking).filter(
        Booking.resource_type == ResourceType.ROOM,
        Booking.resource_id == payload.resource_id,
        Booking.booking_date == payload.booking_date
    ).first()

    if existing_booking:
        if existing_booking.status != BookingStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Переговорная комната уже забронирована на этот день"
            )
        existing_booking.user_id = current_user.id
        existing_booking.status = BookingStatus.PENDING
        db.commit()
        db.refresh(existing_booking)
        return existing_booking

    new_booking = Booking(
        user_id=current_user.id,
        resource_type=ResourceType.ROOM,
        resource_id=payload.resource_id,
        booking_date=payload.booking_date,
        status=BookingStatus.PENDING
    )

    try:
        db.add(new_booking)
        db.commit()
        db.refresh(new_booking)
        return new_booking
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Переговорка уже занята"
        )


@router.post("/{booking_id}/check-in", response_model=BookingResponse)
def check_in_booking(
    booking_id: int,
    db: Session = Depends(get_db)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Бронирование не найдено")

    if booking.status == BookingStatus.CANCELLED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Бронирование отменено")

    booking.status = BookingStatus.CONFIRMED
    db.commit()
    db.refresh(booking)
    return booking


@router.delete("/{booking_id}", response_model=BookingResponse)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Бронирование не найдено")

    if booking.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нельзя отменить чужую бронь")

    booking.status = BookingStatus.CANCELLED
    db.commit()
    db.refresh(booking)
    return booking

