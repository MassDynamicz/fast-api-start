# config/settings.py
import sys
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from config.middleware import add_cors_middleware
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from api.auth.models import User, Role
from .utils import get_password_hash
from datetime import datetime
from config.db import async_session

# Добавьте корневую директорию проекта в путь поиска модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Папка с шаблонами
templates = Jinja2Templates(directory="templates")

async def create_initial_user():
    async with async_session() as session:
        async with session.begin():
            # Проверяем, существует ли начальный пользователь-администратор
            result = await session.execute(
                select(User).filter_by(username="admin", email="admin@example.com")
            )
            initial_user = result.scalars().first()

            if not initial_user:
                # Создаем роль администратора, если она не существует
                result = await session.execute(
                    select(Role).filter_by(name="admin")
                )
                admin_role = result.scalars().first()

                if not admin_role:
                    admin_role = Role(name="admin", description="Администраторы")
                    session.add(admin_role)
                    await session.commit()

                # Создаем начального пользователя-администратора
                initial_user = User(
                    username="admin",
                    first_name="",
                    last_name="",
                    email="admin@mail.com",
                    phone="",
                    address="Almaty",
                    company="Admin Company",
                    is_active=True,
                    is_admin=True,
                    last_login_at=datetime.utcnow(),
                    hashed_password=get_password_hash("admin"),
                    roles=[admin_role]
                )
                session.add(initial_user)
                try:
                    await session.commit()
                    print("Initial admin user created.")  # Пользователь-администратор создан
                except IntegrityError:
                    await session.rollback()
                    print("Initial admin user already exists.")

def create_app() -> FastAPI:
    app = FastAPI(title="Expeditor")

    # Добавление CORS middleware
    add_cors_middleware(app)

    # Подключение статических файлов
    app.mount("/static", StaticFiles(directory="static"), name="static")
    app.mount("/templates", StaticFiles(directory="templates"), name="templates")
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

    # Обработчик для ошибки 404
    @app.exception_handler(404)
    async def not_found_exception_handler(request: Request, exc: HTTPException):
        return templates.TemplateResponse(
            "layouts/errors.html",
            {"request": request, "status_code": 404, "message": "Страница не найдена"},
            status_code=404,
        )

    # Вызов асинхронной функции для создания первичного пользователя
    @app.on_event("startup")
    async def startup_event():
        await create_initial_user()

    return app

app = create_app()
