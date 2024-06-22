#auth/routes/sessions.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from config.db import get_db
from .. import models, schemas
from ..schemas import UserSessionBase
from typing import List

router = APIRouter()

@router.post("/users/{user_id}/sessions/", response_model=schemas.UserSession)
def create_user_session(user_id: int, session: UserSessionBase, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_session = models.UserSession(user_id=user_id, **session.dict())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

@router.get("/users/{user_id}/sessions/", response_model=List[schemas.UserSession])
def read_user_sessions(user_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    sessions = db.query(models.UserSession).filter(models.UserSession.user_id == user_id).offset(skip).limit(limit).all()
    return sessions

@router.delete("/users/{user_id}/sessions/{session_id}", response_model=schemas.UserSession)
def end_user_session(user_id: int, session_id: int, db: Session = Depends(get_db)):
    db_session = db.query(models.UserSession).filter(models.UserSession.user_id == user_id, models.UserSession.id == session_id).first()
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    db_session.session_end = func.now()
    db.commit()
    db.refresh(db_session)
    return db_session
