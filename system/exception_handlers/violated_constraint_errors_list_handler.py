from fastapi import Request, HTTPException, status

from app import app
from exceptions import ViolatedConstraintErrorsList


@app.exception_handler(ViolatedConstraintErrorsList)
def violated_constraint_errors_list_handler(request: Request, exc: ViolatedConstraintErrorsList):
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.errors)
