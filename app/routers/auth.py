from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Team
from app.schemas import UserResponse, TeamResponse

router = APIRouter(prefix="/auth", tags=["Аутентификация и пользователи"])


@router.get("/users", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@router.get("/teams", response_model=List[TeamResponse])
def get_all_teams(db: Session = Depends(get_db)):
    return db.query(Team).all()