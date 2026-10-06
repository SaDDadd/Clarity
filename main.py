from api.v1.auth import router as router_auth
from api.v1.projects import router as router_projects
from api.v1.tasks import router as router_tasks
from api.v1.invitations import router as router_invitations
from api.v1.user import router as router_user
from fastapi import FastAPI
from core.exceptions import register_exception_handlers
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager
from cache.redis_client import close_redis_client, redis_health
from core.database import engine
from core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_redis_client()
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.get('/health', tags=['Сервер'], summary='Проверка работы redis')
async def health():
    return await redis_health()


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list, # Хост фронтенда
    allow_methods=['*'], # Разрешить все методы
    allow_headers=['*'], #  Разрешить все заголовки
    allow_credentials=True # Разрешить передачу учетных данных
)

app.include_router(router_auth, prefix='/api/v1')
app.include_router(router_projects, prefix='/api/v1')
app.include_router(router_tasks, prefix='/api/v1')
app.include_router(router_invitations, prefix='/api/v1')
app.include_router(router_user, prefix='/api/v1')
register_exception_handlers(app)

if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)