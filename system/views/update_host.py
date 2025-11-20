from time import time

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import app
from context import postgres_session, entity_cache
from entities import Host
from repositories import UserRepository, HostRepository
from dependencies import get_session
from schemas.request import UpdateHostRequestSchema
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
    status_code=status.HTTP_200_OK,
    methods=["PUT", "PATCH"]
)
async def update_host(payload: UpdateHostRequestSchema, session: AsyncSession = Depends(get_session)):
    entity_cache.set({})
    postgres_session.set(session)

    user_repository = UserRepository()
    host_repository = HostRepository()

    host = await host_repository.get_by_id(payload.id, for_update=True)
    if not host:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=["Host not found"])

    user = await user_repository.get_by_id(host.user_id, for_update=True)

    _time = int(time())
    await host_repository.fetch_related(host)
    host.store_prev_data()
    host.update(updated_at=_time, **payload.model_dump(exclude_unset=True))
    host.update_related()
    host.fill_from_related()

    await host_repository.violated_constraints(host)

    host.verify()

    await user_repository.save(user)
    await host_repository.save(host)
    await session.commit()

    return HostResponseSchema.model_validate(host)
