from api.v1.auth import router
from fastapi import FastAPI
from core.exceptions import register_exception_handlers

app = FastAPI()

app.include_router(router)
register_exception_handlers(app)