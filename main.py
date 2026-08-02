from api.v1.auth import router as user_registration
from fastapi import FastAPI
from core.exceptions import register_exception_handlers

app = FastAPI()

def main():
    app.include_router(user_registration)
    register_exception_handlers(app)

if __name__ == '__main__':
    main()