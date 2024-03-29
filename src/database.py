from typing import Any

import asyncpg as apg

from config import DB_NAME, DB_HOST, DB_PASS, DB_PORT, DB_USER


class Database:
    """
    Класс Database является обёрткой над драйвером asyncpg.

    Все взаимодействия с базой данных рекомендуется проводить через
    неё, так как помимо сокращения количества уровней вложенности в
    коде за счет автоматической работы с контекстными менеджерами, само
    приложение подразумевает использование пула подключений, чем эта
    обёртка и занимается.

    Например:

    Вместо
    .. code-block:: python
        async with conn_pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute('''
                    INSERT INTO my_table (a) VALUES ($1), ($2)
                ''', 10, 20)
        INSERT 0 2

    Использовать
        await db_instance.execute('''
            INSERT INTO my_table (a) VALUES ($1), ($2)
            ''', 10, 20)
        INSERT 0 2
        ...
    
    """
    
    def __init__(self, host: str, port: str, user: str,
                 password: str, database: str):
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._database = database
        self._connection_pool = None
    
    async def get_connection_pool(self) -> apg.Pool:
        if not self._connection_pool:
            self._connection_pool = await apg.create_pool(
                host=self._host,
                port=self._port,
                user=self._user,
                password=self._password,
                database=self._database,
                min_size=1,
                max_size=5
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


db_instance: Database = Database(DB_HOST, DB_PORT, DB_USER,
                                 DB_PASS, DB_NAME)
