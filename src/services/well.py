from typing import Any
from uuid import UUID

import numpy as np
import asyncpg.exceptions as apg_exc

import services.exceptions as exc
from database import db_instance


async def well_create(
        well_name: str,
        well_head: tuple[np.float32, np.float32],
        md: np.ndarray[np.float32],
        x: np.ndarray[np.float32],
        y: np.ndarray[np.float32],
        z: np.ndarray[np.float32]) -> UUID:
    if not (md.size == x.size == y.size == z.size):
        raise exc.ArrayDifferentSizesException()
    if well_head[0] != x[0] or well_head[1] != y[0]:
        raise exc.InconsistentHeadAndFirstNodeException()

    pool = await db_instance.get_connection_pool()

    async with pool.acquire() as conn:
        async with conn.transaction():
            try:
                well_id = await conn.fetchval(
                    '''
                    SELECT insert_well(
                        $1,
                        $2,
                        $3::double precision[],
                        $4::double precision[],
                        $5::double precision[],
                        $6::double precision[]
                    )
                    ''',
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
            deleted: bool = await conn.fetchval('SELECT delete_well($1)', uuid)

    if not deleted:
        raise exc.WellNotFoundException()


async def well_get(uuid: UUID, return_trajectory: bool = False) -> dict:
    pool = await db_instance.get_connection_pool()
    columns: str = 'name, head, "MD", "X", "Y", "Z"' if return_trajectory else 'name, head'
    trajectory_subquery: str = '''
        , (SELECT array_agg(md) as "MD", array_agg(x) as "X", array_agg(y) as "Y", array_agg(z) as "Z"
        FROM trajectory
        WHERE fk_well_id = $1)''' if return_trajectory else ''

    async with pool.acquire() as conn:
        async with conn.transaction():
            # about 140 ms
            query = await conn.fetchrow(
                f'''
                SELECT {columns}
                FROM well {trajectory_subquery}
                WHERE pk_id = $1
                ''',
                uuid
            )

    if not query:
        raise exc.WellNotFoundException()

    return dict(query)


async def well_at(uuid: UUID, md: float) -> tuple[float, float, float]:
    pool = await db_instance.get_connection_pool()

    async with pool.acquire() as conn:
        async with conn.transaction():
            well_trajectory = await conn.fetchrow(
                f'''
                SELECT ARRAY_AGG(md) as md, ARRAY_AGG(x) as x, ARRAY_AGG(y) as y, ARRAY_AGG(z) as z
                FROM trajectory
                WHERE fk_well_id = $1
                ''',
                uuid
            )

    if not well_trajectory:
        raise exc.WellNotFoundException()

    well_md: np.ndarray[Any, np.dtype[np.float32]] = np.asarray(
        well_trajectory['md'],
        dtype=np.float32
    )

    x: float = float(np.interp(md, well_md, well_trajectory['x']))
    y: float = float(np.interp(md, well_md, well_trajectory['y']))
    z: float = float(np.interp(md, well_md, well_trajectory['z']))

    return x, y, z
