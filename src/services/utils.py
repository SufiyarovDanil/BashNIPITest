import asyncpg as apg
import pandas as pd


async def fetch_as_dataframe(
    connection: apg.Connection,
    query: str,
    *args
) -> pd.DataFrame:
    stmt = await connection.prepare(query)
    columns = [i.name for i in stmt.get_attributes()]
    data = await stmt.fetch(*args)

    return pd.DataFrame(data, columns=columns)
