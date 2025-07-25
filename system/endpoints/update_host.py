from time import time

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app import app
from db import get_session
from context import postgres_session, entity_cache
from entities import Host
from repositories import UserRepository, HostRepository
from decorators import format_response
from formatters import (
    format_payload,
    format_errors,
    format_violated_constraint_errors,
    format_verification_errors
)
from payload_structures import update_host_structure


@app.api_route("/hosts", methods=["PUT", "PATCH"])
@format_response
async def update_host(request: Request, session: AsyncSession = Depends(get_session)) -> tuple[dict, int]:
    entity_cache.set({})
    postgres_session.set(session)

    payload = await request.json()
    formatted_payload, errors = format_payload(payload, update_host_structure)
    if errors:
        return format_errors(errors, 400)

    user_repository = UserRepository()
    host_repository = HostRepository()

    host = await host_repository.get_by_id(formatted_payload["id"], for_update=True)
    if not host:
        return format_errors(["Host not found"], 404)

    user = await user_repository.get_by_id(host.user_id, for_update=True)

    _time = int(time())
    await host_repository.fetch_related(host)
    host.store_prev_data()
    host.update(updated_at=_time, **formatted_payload)
    host.update_related()
    host.fill_from_related()

    errors = await host_repository.violated_constraints(host)
    if errors:
        return format_violated_constraint_errors(errors)
    errors = host.verify()
    if errors:
        return format_verification_errors(errors)

    await user_repository.save(user)
    await host_repository.save(host)
    await session.commit()

    return host.data, 200
