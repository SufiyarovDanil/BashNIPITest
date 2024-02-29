import asyncpg
from asyncpg.connection import Connection
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)

from config import (
    DB_NAME,
    DB_HOST,
    DB_PASS,
    DB_PORT,
    DB_USER
)


__POSTGRES_URI: str = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
__ALCHEMY_URI: str = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'


async def make_apg_connection() -> Connection:
    return await asyncpg.connect(__POSTGRES_URI)


async_engine: AsyncEngine = create_async_engine(
    url=__ALCHEMY_URI,
    echo=True
)

async_session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(async_engine)
