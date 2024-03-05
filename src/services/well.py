from uuid import UUID
import numpy as np
import asyncpg.exceptions as apg_exc
import time

from . import exceptions as exc
from database import db_instance


async def well_create(
    well_name: str,
    well_head: tuple[np.float32, np.float32],
    md: np.ndarray[np.float32],
    x: np.ndarray[np.float32],
    y: np.ndarray[np.float32],
    z: np.ndarray[np.float32]
) -> UUID:
    if not (md.size == x.size == y.size == z.size):
        raise exc.ArrayDifferentSizesException()
    if well_head[0] != x[0] or well_head[1] != y[0]:
        raise exc.InconsistentHeadAndFirstNodeException()
    
    pool = await db_instance.get_connection_pool()

    async with pool.acquire() as conn:
        async with conn.transaction():
            try:
                await conn.execute(
                    'INSERT INTO well(pk_id, name, head) VALUES (gen_random_uuid(), $1, $2)',
                    well_name,
                    well_head
                )

                well_id: UUID = await conn.fetchval(
                    'SELECT pk_id FROM well WHERE name = $1',
                    well_name
                )

                trajectory_data = [(i[0], i[1], i[2], i[3]) for i in np.column_stack((md, x, y, z))]

                await conn.execute(
                    f'''
                    CREATE TABLE trajectory_{well_id.hex}
                    (
                        pk_id bigserial,
                        md double precision NOT NULL,
                        x double precision NOT NULL,
                        y double precision NOT NULL,
                        z double precision NOT NULL,
                        PRIMARY KEY (pk_id)
                    )
                    '''
                )

                await conn.executemany(
                    f'INSERT INTO trajectory_{well_id.hex}(md, x, y, z) VALUES ($1, $2, $3, $4)',
                    trajectory_data
                )
            except apg_exc.UniqueViolationError:
                raise exc.WellAlreadyExistsException()

    return well_id


async def well_remove(uuid: UUID) -> None:
    pool = await db_instance.get_connection_pool()

    async with pool.acquire() as conn:
        async with conn.transaction():
            stmt = await conn.execute(
                'DELETE FROM well WHERE pk_id = $1',
                uuid
            )

            if stmt == 'DELETE 0':
                raise exc.WellNotFoundException()
            
            await conn.execute(f'DROP TABLE trajectory_{uuid.hex}')
            


async def well_get(uuid: UUID, return_trajectory: bool = False) -> dict:
    pool = await db_instance.get_connection_pool()
    columns = 'name, head, "MD", "X", "Y", "Z"' if return_trajectory else 'name, head'
    trajectory_subquery = f'''
        , (
	        SELECT ARRAY_AGG(md) as "MD", ARRAY_AGG(x) as "X", ARRAY_AGG(y) as "Y", ARRAY_AGG(z) as "Z"
	        FROM trajectory_{uuid.hex}
        )
    ''' if return_trajectory else ''
    sql: str = f'''
        SELECT {columns}
            FROM well {trajectory_subquery}
            WHERE pk_id = $1'''
    
    async with pool.acquire() as conn:
        async with conn.transaction():
            start = time.time()
            query = await conn.fetchrow(sql, uuid)
            end = time.time()
            print(end - start)

    if not query:
        raise exc.WellNotFoundException()

    return dict(query)


async def well_at(uuid: UUID, md: float) -> tuple[float, float, float]:
    well: dict = await well_get(uuid, True)

    x: float = np.interp([md], well['MD'], well['X'])[0]
    y: float = np.interp([md], well['MD'], well['Y'])[0]
    z: float = np.interp([md], well['MD'], well['Z'])[0]

    return (x, y, z)
