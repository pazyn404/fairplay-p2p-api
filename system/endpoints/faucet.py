from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import app
from db import get_session
from models import UserModel


@app.api_route("/faucet/{id}", methods=["POST"])
async def faucet(id: int, session: AsyncSession = Depends(get_session)) -> dict:
    user = await session.get(UserModel, id)
    user.balance += 100
    await session.commit()

    return {200: "ok"}
