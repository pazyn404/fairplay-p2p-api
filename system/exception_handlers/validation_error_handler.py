from fastapi import Request, HTTPException, status
from pydantic import ValidationError

from app import app


@app.exception_handler(ValidationError)
def validation_error_handler(request: Request, exc: ValidationError):
    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.errors())
