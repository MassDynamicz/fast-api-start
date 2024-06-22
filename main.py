# main.py
from fastapi import Request, Form, HTTPException, status
from config.settings import app, templates
from api.auth.routes.users import router as users_router
from api.auth.routes.sessions import router as sessions_router
from api.auth.routes.roles import router as roles_router
from fastapi.responses import JSONResponse

app.include_router(users_router, prefix="/users",tags=["Пользователи"])
app.include_router(sessions_router, prefix="/sessions",tags=["Сессии"])
app.include_router(roles_router, prefix="/roles", tags=["Роли"])

# root
@app.get("/", tags=["Шаблоны"])
async def read_root(request: Request):
    data = {"request": request, "title": 'Главная Expeditor'}
    return templates.TemplateResponse("index.html", data)

# @app.get("/login/", tags=["Авторизация"])
# async def login_page(request: Request):
#     data = {"request": request, "title": 'Страница авторизации'}
#     return templates.TemplateResponse("/users/login.html", data)

@app.post("/login/", tags=["Авторизация"])
async def login_for_access_token(request: Request, username: str = Form(...), password: str = Form(...)):
    user = fake_users_db.get(username)
    if not user or user["password"] != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    # Возвращаем простой токен
    return JSONResponse(content={"access_token": user["token"], "token_type": "bearer"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)