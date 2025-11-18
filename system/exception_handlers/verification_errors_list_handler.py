from fastapi import Request, HTTPException, status

from app import app
from exceptions import VerificationErrorsList


@app.exception_handler(VerificationErrorsList)
def verification_errors_list_handler(request: Request, exc: VerificationErrorsList):
    raise HTTPException(status_code=exc.status_code, detail=exc.errors)
