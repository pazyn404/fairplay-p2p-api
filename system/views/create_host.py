from time import time

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import app
from context import postgres_session, entity_cache
from entities import Host
from repositories import UserRepository, HostRepository
from dependencies import get_session
from schemas.request import CreateHostRequestSchema
from schemas.response import HostResponseSchema, ErrorResponseSchema


@app.api_route(
    "/hosts",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponseSchema},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponseSchema},
        status.HTTP_409_CONFLICT: {"model": ErrorResponseSchema}
    },
    response_model=HostResponseSchema,
    response_model_by_alias=False,
    status_code=status.HTTP_201_CREATED,
    methods=["POST"]
)
async def create_host(payload: CreateHostRequestSchema, session: AsyncSession = Depends(get_session)):
    entity_cache.set({})
    postgres_session.set(session)

    user_repository = UserRepository()
    host_repository = HostRepository()

    user = await user_repository.get_by_id(payload.user_id, for_update=True)
    if not user:
        raise HTTPException(status_code=404, detail=["User not found"])

    _time = int(time())
    host = Host(created_at=_time, updated_at=_time, **payload.model_dump())
    await host_repository.fetch_related(host)
    host.update_related()
    host.fill_from_related()

    await host_repository.violated_constraints(host)

    host.verify()

    await user_repository.save(user)
    await host_repository.save(host)
    await session.commit()

    return HostResponseSchema.model_validate(host)
