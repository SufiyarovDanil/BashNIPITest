from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from endpoints.exception_handlers import validation_exception_handler
from endpoints.well import router as well_router


app: FastAPI = FastAPI(
    title='Well API',
    description='API предназачен для управления данными о скважинах.',
    swagger_ui_parameters={
        'displayRequestDuration': True,
        'defaultModelsExpandDepth': 0
    }
)

app.include_router(well_router)
app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler
)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run('__main__:app', host='127.0.0.1', port=8070, reload=True)
