from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import app
from models import UserModel
from dependencies import get_session


@app.api_route("/faucet/{id}", methods=["POST"])
async def faucet(id: int, session: AsyncSession = Depends(get_session)) -> dict[int, str]:
    user = await session.get(UserModel, id)
    user.balance += 100
    await session.commit()

    return {200: "ok"}
