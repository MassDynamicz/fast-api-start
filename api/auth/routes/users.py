from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from config.db import get_db
from api.auth import models, schemas
from config.utils import get_password_hash
from typing import List
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(models.User).filter_by(email=user.email))
        db_user = result.scalars().first()
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        if not user.roles:
            raise HTTPException(status_code=400, detail="User must have at least one role")
        
        roles = []
        for role_id in user.roles:
            role_result = await db.execute(select(models.Role).filter_by(id=role_id))
            role = role_result.scalars().first()
            if not role:
                raise HTTPException(status_code=404, detail=f"Role with id {role_id} not found")
            roles.append(role)
        
        hashed_password = get_password_hash(user.password)
        is_admin = any(role.name == "admin" for role in roles)
        db_user = models.User(
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            address=user.address,
            company=user.company,
            is_active=user.is_active,
            is_admin=is_admin,
            hashed_password=hashed_password,
            last_login_at=datetime.utcnow()
        )
        
        db_user.roles = roles
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return schemas.User.from_orm(db_user)
    except Exception as e:
        print(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/", response_model=List[schemas.User])
async def read_users(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).offset(skip).limit(limit))
    users = result.scalars().all()
    return [schemas.User.from_orm(user) for user in users]

@router.get("/{user_id}", response_model=schemas.User)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).filter_by(id=user_id))
    user = result.scalars().first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return schemas.User.from_orm(user)

@router.put("/{user_id}", response_model=schemas.User)
async def update_user(user_id: int, user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(models.User).filter_by(id=user_id))
        db_user = result.scalars().first()
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        user_data = user.dict(exclude_unset=True)
        
        # Логирование значений, которые будут обновлены
        print(f"Updating user {user_id} with data: {user_data}")

        for key, value in user_data.items():
            if key == "password":
                value = get_password_hash(value)
            setattr(db_user, key, value)

        if "roles" in user_data:
            roles = []
            for role_id in user_data["roles"]:
                role_result = await db.execute(select(models.Role).filter_by(id=role_id))
                role = role_result.scalars().first()
                if not role:
                    raise HTTPException(status_code=404, detail=f"Role with id {role_id} not found")
                roles.append(role)
            db_user.roles = roles
            db_user.is_admin = any(role.name == "admin" for role in roles)

        await db.commit()
        await db.refresh(db_user)
        return schemas.User.from_orm(db_user)
    except Exception as e:
        print(f"Error updating user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.delete("/{user_id}", response_model=schemas.User)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(models.User).filter_by(id=user_id))
        db_user = result.scalars().first()
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        await db.delete(db_user)
        await db.commit()
        return schemas.User.from_orm(db_user)
    except Exception as e:
        print(f"Error deleting user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
