# main.py
from fastapi import Request, HTTPException, status
from config.settings import app, templates
from api.auth.routes.users import router as users_router
from api.auth.routes.roles import router as roles_router
from api.auth.routes.login import router as login_router
from fastapi.responses import JSONResponse

app.include_router(login_router, tags=["Авторизация"])
app.include_router(users_router, prefix="/users",tags=["Пользователи"])
app.include_router(roles_router, prefix="/roles", tags=["Роли и права доступа"])

# root
@app.get("/", tags=["Страницы"])
async def read_root(request: Request):
    data = {"request": request, "title": 'Главная Expeditor'}
    return templates.TemplateResponse("index.html", data)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)