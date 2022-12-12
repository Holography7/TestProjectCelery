from typing import AsyncGenerator

from database import mongo_engine
from odmantic.session import AIOSession


async def get_db_session() -> AsyncGenerator[AIOSession, None]:
    async with mongo_engine.session() as session:
        yield session
