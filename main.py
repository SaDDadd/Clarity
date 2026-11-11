from api.v1.auth import router as router_auth
from api.v1.projects import router as router_projects
from api.v1.tasks import router as router_tasks
from api.v1.invitations import router as router_invitations
from api.v1.user import router as router_user
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
import uvicorn
from cache.redis_client import close_redis_client, redis_health
from core.database import engine
from core.config import settings
from core.dependencies import get_db
from core.exceptions import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управляет жизненным циклом приложения и освобождает ресурсы при остановке."""
    yield
    await close_redis_client()
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.get('/health', tags=['Сервер'], summary='Проверка работы redis')
async def health(db: AsyncSession = Depends(get_db)):
    """Возвращает статус доступности Redis и БД."""
    redis_ok = await redis_health()
    try:
        await db.execute(text('SELECT 1'))
        db_ok = True
    except Exception:
        db_ok = False
    return {'redis': redis_ok['redis'], 'db': 'ok' if db_ok else 'unavailable'}


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