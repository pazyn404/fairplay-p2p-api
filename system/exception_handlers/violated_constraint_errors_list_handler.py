from fastapi import Request, HTTPException

from app import app
from exceptions import ViolatedConstraintErrorsList


@app.exception_handler(ViolatedConstraintErrorsList)
def violated_constraint_errors_list_handler(request: Request, exc: ViolatedConstraintErrorsList):
    raise HTTPException(status_code=exc.status_code, detail=exc.errors)
