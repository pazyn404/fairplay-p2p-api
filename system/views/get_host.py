from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import app
from context import postgres_session
from repositories import HostRepository
from dependencies import get_session
from schemas.response import HostResponseSchema, ErrorResponseSchema


@app.api_route(
    "/hosts/{id}",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponseSchema}
    },
    response_model=HostResponseSchema,
    response_model_by_alias=False,
    methods=["GET"]
)
async def get_host(id: int, session: AsyncSession = Depends(get_session)):
    postgres_session.set(session)

    host_repository = HostRepository()
    host = await host_repository.get_by_id(id, for_update=False)
    if not host:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=["Host not found"])

    await host_repository.fetch_related(host)

    return HostResponseSchema.model_validate(host)
