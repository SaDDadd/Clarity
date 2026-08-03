from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from jose import JWSError
from pydantic import ValidationError

class AppException(Exception): # Общий класс ошибок
    def __init__(self, code, detail):
        self.status_code = code # HTTP статус ошибки
        self.detail = detail # Сообщение для пользователя

class NotFoundException(AppException): # Нет ресурсов
    def __init__(self, detail=None):
        self.status_code = 404
        self.detail = detail
        super().__init__(self.status_code, self.detail)

class PermissionDeniedException(AppException): # Запрет доступа
    def __init__(self, detail=None):
        self.status_code = 403
        self.detail = detail
        super().__init__(self.status_code, self.detail)
        
class ConflictException(AppException): # Конфликты
    def __init__(self, detail=None):
        self.status_code = 409
        self.detail = detail
        super().__init__(self.status_code, self.detail)

class AuthenticationException(AppException): # Ошибка аутентификации
    def __init__(self, detail=None):
        self.status_code = 401
        self.detail = detail
        super().__init__(self.status_code, self.detail)

class LackOfInformayionException(AppException): # Нехватка вводимой информации
    def __init__(self, detail=None):
        self.status_code = 422
        self.detail = detail
        super().__init__(self.status_code, self.detail)
        
def register_exception_handlers(app: FastAPI): # Регистрирует глобальные обработчики для кастомных и стандартных исключений, 
                                        # возвращая JSON-ответы с соответствующими HTTP-статусами.
    @app.exception_handler(NotFoundException)
    def er_not_found_exception(request, exc):
        return JSONResponse(status_code=exc.status_code, content={'detail':exc.detail})

    @app.exception_handler(PermissionDeniedException)
    def er_permission_denied_exception(request, exc):
        return JSONResponse(status_code=exc.status_code, content={'detail':exc.detail})

    @app.exception_handler(ConflictException)
    def er_conflict_exception(request, exc):
        return JSONResponse(status_code=exc.status_code, content={'detail':exc.detail})

    @app.exception_handler(AuthenticationException)
    def er_authentication_exception(request, exc):
        return JSONResponse(status_code=exc.status_code, content={'detail':exc.detail})

    @app.exception_handler(SQLAlchemyError)
    def er_sqlalchemy(request, exc):
        return JSONResponse(status_code=500, content={'detail':'Ошибка базы данных'})

    @app.exception_handler(JWSError)
    def er_jws(request, exc):
        return JSONResponse(status_code=401, content={'detail':'Недействительный токен'})

    @app.exception_handler(ValidationError)
    def er_validation(request, exc):
        return JSONResponse(status_code=422, content={'detail':exc.errors()})

    @app.exception_handler(AppException)
    def er_app(request, exc):
        return JSONResponse(status_code=exc.status_code, content={'detail':exc.detail})