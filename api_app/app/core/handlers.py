from fastapi import Request
from fastapi.responses import JSONResponse
from errors import *


def register_handlers(app):
    @app.exception_handler(CacheError)
    async def csv_handler(request: Request, exc: CacheError):
        return JSONResponse(status_code=400, content={"error": "Cache Error", "detail": exc.message})

    @app.exception_handler(DatabaseError)
    async def not_found_handler(request: Request, exc: DatabaseError):
        return JSONResponse(status_code=404, content={"error": "Database Error", "detail": exc.message})

    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        return JSONResponse(status_code=404, content={"error": "Not Found", "detail": exc.message})

    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        return JSONResponse(status_code=422, content={"error": "Validation Error", "detail": exc.message})
