from fastapi import FastAPI

from endpoints.well import router as well_router


app: FastAPI = FastAPI(
    title='Well API',
    swagger_ui_parameters={ 'displayRequestDuration': True }
)

app.include_router(well_router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('__main__:app', host='127.0.0.1', port=8070, reload=True)
