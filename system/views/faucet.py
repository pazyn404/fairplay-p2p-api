from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import app
from db import get_session
from models import User


@app.api_route("/faucet/{user_id}", methods=["POST"])
async def faucet(user_id: int, session: AsyncSession = Depends(get_session)):
    user = await session.get(User, user_id)
    user.balance += 100
    await session.commit()

    return {200: "ok"}
