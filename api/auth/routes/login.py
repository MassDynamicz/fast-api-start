from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from config.db import get_db
from api.auth.models import User
from config.utils import verify_password
from api.auth.schemas import Login

router = APIRouter()

@router.post("/login/")
async def login(data: Login, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.username == data.username))
    user = result.scalars().first()
    if user is None or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Не правильный логин или пароль")
    return {"detail": "Авторизация прошла успешно"}
