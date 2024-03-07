from uuid import UUID

import numpy as np
import asyncpg.exceptions as apg_exc

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
                well_id: UUID = await conn.fetchval(
                    '''SELECT insert_well(
                        $1,
                        $2,
                        $3::DOUBLE PRECISION[],
                        $4::DOUBLE PRECISION[],
                        $5::DOUBLE PRECISION[],
                        $6::DOUBLE PRECISION[]
                    )''',
                    well_name,
                    well_head,
                    md,
                    x,
                    y,
                    z
                )
            except apg_exc.UniqueViolationError:
                raise exc.WellAlreadyExistsException()

    return well_id


async def well_remove(uuid: UUID) -> None:
    pool = await db_instance.get_connection_pool()

    async with pool.acquire() as conn:
        async with conn.transaction():
            is_deleted: bool = await conn.fetchval(
                'SELECT * FROM delete_well($1)',
                uuid
            )

    if not is_deleted:
        raise exc.WellNotFoundException()


async def well_get(uuid: UUID, return_trajectory: bool = False) -> dict:
    pool = await db_instance.get_connection_pool()
    columns: str = 'name, head, md as "MD", x as "X", y as "Y", z as "Z"' if return_trajectory else 'name, head'

    async with pool.acquire() as conn:
        async with conn.transaction():
            try:
                query = await conn.fetchrow(
                    f'''SELECT {columns}
                    FROM well_{uuid.hex}'''
                )
            except apg_exc.UndefinedTableError:
                raise exc.WellNotFoundException()

    if not query:
        raise exc.WellNotFoundException()

    return dict(query)


async def well_at(uuid: UUID, md: float) -> tuple[float, float, float]:
    pool = await db_instance.get_connection_pool()

    async with pool.acquire() as conn:
        async with conn.transaction():
            try:
                well_trajectory = await conn.fetchrow(
                    f'''
                    SELECT md, x, y, z
                    FROM well_{uuid.hex}
                    '''
                )
            except apg_exc.UndefinedTableError:
                raise exc.WellNotFoundException()
    
    if not well_trajectory:
        raise exc.WellNotFoundException()

    md_array: np.ndarray = np.asarray(well_trajectory['md'])

    x: float = np.interp(md, md_array, well_trajectory['x'])
    y: float = np.interp(md, md_array, well_trajectory['y'])
    z: float = np.interp(md, md_array, well_trajectory['z'])

    return x, y, z
