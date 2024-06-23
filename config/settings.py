# config/settings.py
import sys
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from config.middleware import add_cors_middleware
from dotenv import load_dotenv
from api.auth.routes.users import create_initial_user
from config.db import async_session
from fastapi.responses import JSONResponse

# Добавьте корневую директорию проекта в путь поиска модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Папка с шаблонами
templates = Jinja2Templates(directory="templates")

# Загрузить переменные окружения из .env файла
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

SECRET_KEY = os.getenv("SECRET_KEY", os.urandom(32).hex())
ALGORITHM = "HS256"

def create_app() -> FastAPI:
    app = FastAPI(title="Expeditor")

    # Добавление CORS middleware
    add_cors_middleware(app)

    # Подключение статических файлов
    app.mount("/static", StaticFiles(directory="static"), name="static")


    # Обработчик для ошибки 404
    @app.exception_handler(404)
    async def not_found_exception_handler(request: Request, exc: HTTPException):
        return templates.TemplateResponse(
            "layouts/errors.html",
            {"request": request, "status_code": 404, "message": "Страница не найдена"},
            status_code=404,
        )
    # Обработчик для ошибки 400
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
    # Вызов асинхронной функции для создания первичного пользователя
    @app.on_event("startup")
    async def startup_event():
        async with async_session() as session:
            await create_initial_user(session)

    return app

app = create_app()
