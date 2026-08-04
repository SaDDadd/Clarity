from api.v1.auth import router as router_user
from api.v1.projects import router as router_projects
from fastapi import FastAPI
from core.exceptions import register_exception_handlers
import uvicorn

app = FastAPI()

app.include_router(router_user, prefix='/api/v1')
app.include_router(router_projects, prefix='/api/v1')
register_exception_handlers(app)

if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)