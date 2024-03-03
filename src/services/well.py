from uuid import UUID
import numpy as np
import asyncpg.exceptions as apg_exc

from . import exceptions as exc
from database import db_instance

import time

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
            stmt = await conn.execute('CALL delete_well($1)', uuid)

    if stmt == 'DELETE 0':
        raise exc.WellNotFoundException()


async def well_get(uuid: UUID, return_trajectory: bool = False) -> dict:
    pool = await db_instance.get_connection_pool()

    async with pool.acquire() as conn:
        async with conn.transaction():
            columns: str = 'name, head, md, x, y, z' if return_trajectory else 'name, head'
            # about 400 - 450 ms
            start = time.time()
            query = await conn.fetch(
                f'''
                SELECT {columns}
                FROM well
                {'JOIN trajectory ON fk_well_id = $1' if return_trajectory else ''}
                WHERE well.pk_id = $1''',
                uuid
            )
            print('elapsed time', time.time() - start)

    if not query:
        raise exc.WellNotFoundException()
    
    result: dict = {
        'name': query[0]['name'],
        'head': (query[0]['head'].x, query[0]['head'].y)
    }
    
    if return_trajectory:
        transparent_trajectory: np.ndarray = np.array([[i['md'], i['x'], i['y'], i['z']] for i in query]).T
        result['MD'] = transparent_trajectory[0].tolist()
        result['X'] = transparent_trajectory[1].tolist()
        result['Y'] = transparent_trajectory[2].tolist()
        result['Z'] = transparent_trajectory[3].tolist()

    return result


async def well_at(uuid: UUID, md: float) -> tuple[float, float, float]:
    well: dict = await well_get(uuid, True)

    x: float = np.interp([md], well['MD'], well['X'])[0]
    y: float = np.interp([md], well['MD'], well['Y'])[0]
    z: float = np.interp([md], well['MD'], well['Z'])[0]

    return (x, y, z)
