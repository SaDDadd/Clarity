import json
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from jose import JWSError
from pydantic import ValidationError
import logging

class AppException(Exception): 
    """"""
    def __init__(self, code, detail):
        self.status_code = code
        self.detail = detail
        super().__init__(detail)

class NotFoundException(AppException): 
    """"""
    def __init__(self, detail=None):
        self.status_code = 404
        self.detail = detail
        super().__init__(self.status_code, self.detail)

class PermissionDeniedException(AppException):
    """"""
    def __init__(self, detail=None):
        self.status_code = 403
        self.detail = detail
        super().__init__(self.status_code, self.detail)
        
class ConflictException(AppException):
    """"""
    def __init__(self, detail=None):
        self.status_code = 409
        self.detail = detail
        super().__init__(self.status_code, self.detail)

class AuthenticationException(AppException):
    """"""
    def __init__(self, detail=None):
        self.status_code = 401
        self.detail = detail
        super().__init__(self.status_code, self.detail)

class LackOfInformationException(AppException): 
    """"""
    def __init__(self, detail=None):
        self.status_code = 422
        self.detail = detail
        super().__init__(self.status_code, self.detail)

class InvitationAlreadyProcessedException(AppException): 
    """"""
    def __init__(self, detail=None):
        self.status_code = 409
        self.detail = detail 
        super().__init__(self.status_code, self.detail)

class InvalidInvitationStateException(AppException): 
    """"""
    def __init__(self, detail=None):
        self.status_code = 400
        self.detail = detail 
        super().__init__(self.status_code, self.detail)

class LastAdminDeletionException(AppException): 
    """"""
    def __init__(self, detail=None):
        self.status_code = 400
        self.detail = detail 
        super().__init__(self.status_code, self.detail)

class MemberAlreadyInProjectException(AppException):
    """"""
    def __init__(self, detail=None):
        self.status_code = 409
        self.detail = detail
        super().__init__(self.status_code, self.detail)

class InvalidDeadlineException(AppException):
    """"""
    def __init__(self, detail=None):
        self.status_code = 422
        self.detail = detail
        super().__init__(self.status_code, self.detail)

class TaskAssignmentException(AppException): 
    """"""
    def __init__(self, detail=None):
        self.status_code = 403
        self.detail = detail
        super().__init__(self.status_code, self.detail)

class TokenExpiredException(AppException):
    """"""
    def __init__(self, detail=None):
        self.status_code = 401
        self.detail = detail
        super().__init__(self.status_code, self.detail)

class InvalidTokenException(AppException):
    """"""
    def __init__(self, detail=None):
        self.status_code = 401
        self.detail = detail
        super().__init__(self.status_code, self.detail)

class PaginationException(AppException):
    """"""
    def __init__(self, detail=None):
        self.status_code = 422
        self.detail = detail
        super().__init__(self.status_code, self.detail)

class UnprocessableEntityException(AppException):
    """"""
    def __init__(self, detail=None):
        self.status_code = 422
        self.detail = detail
        super().__init__(self.status_code, self.detail)

def register_exception_handlers(app: FastAPI):
    """"""
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
        logging.error("SQLAlchemy error occurred", exc_info=exc)
        return JSONResponse(status_code=500, content={'detail':'Ошибка базы данных'})

    @app.exception_handler(JWSError)
    def er_jws(request, exc):
        return JSONResponse(status_code=401, content={'detail':'Недействительный токен'})

    @app.exception_handler(ValidationError)
    def er_validation(request, exc: ValidationError):
        return JSONResponse(status_code=422, content={'detail': json.loads(exc.json())})

    @app.exception_handler(AppException)
    def er_app(request, exc):
        return JSONResponse(status_code=exc.status_code, content={'detail':exc.detail})