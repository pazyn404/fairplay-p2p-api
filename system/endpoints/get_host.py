from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import app
from db import get_session
from context import postgres_session
from repositories import HostRepository
from decorators import format_response
from formatters import format_errors



@app.api_route("/hosts/{id}", methods=["GET"])
@format_response
async def get_host(id: int, session: AsyncSession = Depends(get_session)) -> tuple[dict, int]:
    postgres_session.set(session)

    host_repository = HostRepository()
    host = await host_repository.get_by_id(id, for_update=False)
    if not host:
        return format_errors(["Host not found"], 404)

    await host_repository.fetch_related(host)

    return host.data, 200
