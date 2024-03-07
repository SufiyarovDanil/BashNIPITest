from typing import Any

import asyncpg as apg

from config import DB_NAME, DB_HOST, DB_PASS, DB_PORT, DB_USER


async def make_apg_connection() -> apg.Connection:
    return await apg.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )


class Database:
    def __init__(self):
        self._connection_pool = None
    
    async def get_connection_pool(self) -> apg.Pool:
        if not self._connection_pool:
            self._connection_pool = await apg.create_pool(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASS,
                database=DB_NAME,
                min_size=1,
                max_size=10
            )
        
        return self._connection_pool

    async def execute(self, query: str, *args) -> apg.Record:
        pool: apg.Pool = await self.get_connection_pool()

        async with pool.acquire() as conn:
            async with conn.transaction():
                result: apg.Record = await conn.execute(query, *args)

        return result

    async def executemany(self, query: str, *args) -> apg.Record:
        pool: apg.Pool = await self.get_connection_pool()

        async with pool.acquire() as conn:
            async with conn.transaction():
                result: apg.Record = await conn.executemany(query, *args)

        return result

    async def fetch(self, query: str, *args) -> apg.Record:
        pool: apg.Pool = await self.get_connection_pool()

        async with pool.acquire() as conn:
            async with conn.transaction():
                result: apg.Record = await conn.fetch(query, *args)

        return result

    async def fetch_row(self, query: str, *args) -> apg.Record:
        pool: apg.Pool = await self.get_connection_pool()

        async with pool.acquire() as conn:
            async with conn.transaction():
                result: apg.Record = await conn.fetchrow(query, *args)

        return result

    async def fetch_val(self, query: str, *args) -> Any:
        pool: apg.Pool = await self.get_connection_pool()

        async with pool.acquire() as conn:
            async with conn.transaction():
                result: Any = await conn.fetchval(query, *args)

        return result


db_instance: Database = Database()
