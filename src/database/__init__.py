import asyncpg
from asyncpg.connection import Connection

from config import (
    DB_NAME,
    DB_HOST,
    DB_PASS,
    DB_PORT,
    DB_USER
)


async def make_apg_connection() -> Connection:
    return await asyncpg.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )


class Database:
    def __init__(self):
        self._connection_pool = None
    
    async def get_connection_pool(self) -> asyncpg.Pool:
        if not self._connection_pool:
            self._connection_pool = await asyncpg.create_pool(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASS,
                database=DB_NAME,
                min_size=1,
                max_size=10
            )
        
        return self._connection_pool


db_instance: Database = Database()
