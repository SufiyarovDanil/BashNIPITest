from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from schemas.well import WellOutputSchema


async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError):
    """
    Кастомный хэндлер для ошибок валидации входных данных.

    Нужен для соблюдения общего формата ответа.

    """
    
    error = exc.errors()[0]

    content: WellOutputSchema = WellOutputSchema(
        data={'arg': error['loc']},
        error=error["msg"]
    )

    return JSONResponse(jsonable_encoder(content))
