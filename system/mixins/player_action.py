from abc import abstractmethod

from config import VerificationError
from sqlalchemy import select
from utils import sign


class PlayerActionMixin:
    FOR_HOST_DATA_ATTRIBUTES = ["game_id", "created_at", "system_signature|for_host_signature"]
    FOR_HOST_SIGNATURE_ATTRIBUTES = [
        "action_number|{GAME_MODEL}:game_id.User:user_id.action_number", "game_id", "game_name|{GAME_MODEL}.GAME_NAME",
        "game_revision|{GAME_MODEL}:game_id.action_number", "game_action_number|{GAME_MODEL}:game_id.actions_count", "created_at"
    ]

    @abstractmethod
    async def is_last_action(self):
        raise NotImplementedError

    async def is_first_action(self):
        game = await self.session.get(self.__class__.GAME_MODEL, self.game_id)

        return game.actions_count == 1

    @property
    async def for_host_data(self):
        return await self._parse_attrs(self.__class__.FOR_HOST_DATA_ATTRIBUTES)

    @property
    async def for_host_signature_data(self):
        return await self._parse_attrs(self.__class__.FOR_HOST_SIGNATURE_ATTRIBUTES)

    @property
    async def for_host_signature(self):
        data = await self.for_host_signature_data
        signature = sign(data)

        return signature

    async def verify_player_balance(self):
        from models import User

        game = await self.session.get(self.__class__.GAME_MODEL, self.game_id)
        if game.player_id is not None:
            return

        user = await self.session.get(User, self.user_id)
        if user.balance < game.bet:
            raise VerificationError("Insufficient balance", 409)

    async def verify_player_host_unset(self):
        from models import Host

        query = select(Host).filter_by(user_id=self.user_id)
        res = await self.session.execute(query)
        host = res.scalars().first()
        if host:
            raise VerificationError("You can't play from an account where a host is set", 409)

    async def verify_player(self):
        game = await self.session.get(self.__class__.GAME_MODEL, self.game_id)

        if game.player_id is not None and game.player_id != self.user_id:
            raise VerificationError("You are not player of this game", 409)

    async def verify_host_active(self):
        from models import Host

        game = await self.session.get(self.__class__.GAME_MODEL, self.game_id)
        query = select(Host).filter_by(user_id=game.user_id)
        res = await self.session.execute(query)
        host = res.scalars().first()
        if not host.active:
            raise VerificationError("Host is not active", 409)

    async def verify_game_active(self):
        game = await self.session.get(self.__class__.GAME_MODEL, self.game_id)
        if not game.active:
            raise VerificationError("Game is not active", 409)

    async def verify_game_not_complete(self):
        game = await self.session.get(self.__class__.GAME_MODEL, self.game_id)
        if game.winner_id is not None or (game.started_at is not None and game.started_at + game.duration < self.created_at):
            raise VerificationError("Game is already complete", 409)

    async def update_related_player_balance(self):
        from models import User

        if await self.is_first_action():
            user = await self.session.get(User, self.user_id)
            game = await self.session.get(self.__class__.GAME_MODEL, self.game_id)

            user.balance -= game.bet

    async def update_related_game_ownership(self):
        from models import User

        if await self.is_first_action():
            user = await self.session.get(User, self.user_id)
            game = await self.session.get(self.__class__.GAME_MODEL, self.game_id)

            game.player_id = user.id

    async def update_related_game_started_time(self):
        if await self.is_first_action():
            game = await self.session.get(self.__class__.GAME_MODEL, self.game_id)
            game.started_at = self.created_at

    async def update_related_game_finished_time(self):
        if await self.is_last_action():
            game = await self.session.get(self.__class__.GAME_MODEL, self.game_id)
            game.finished_at = self.created_at
