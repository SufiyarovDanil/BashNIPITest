from uuid import UUID
import numpy as np
import asyncpg.exceptions as apg_exc

from . import exceptions as exc
from database import make_apg_connection


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
    
    conn = await make_apg_connection()

    try:
        await conn.execute(
            'INSERT INTO well(pk_id, name, head) VALUES (gen_random_uuid(), $1, $2)',
            well_name,
            well_head
        )

        well_id = await conn.fetchval(
            'SELECT pk_id FROM well WHERE name = $1',
            well_name
        )

        trajectory_data = [(i[0], i[1], i[2], i[3], well_id) for i in np.column_stack((md, x, y, z))]
        
        await conn.executemany(
            f'INSERT INTO trajectory(md, x, y, z, fk_well_id) VALUES ($1, $2, $3, $4, $5)',
            trajectory_data
        )
    except apg_exc.UniqueViolationError:
        raise exc.WellAlreadyExistsException()
    
    await conn.close()

    return well_id


async def well_remove(uuid: UUID) -> None:
    conn = await make_apg_connection()
    stmt = await conn.execute(
        'DELETE FROM well WHERE pk_id = $1',
        uuid
    )
    await conn.close()

    if stmt == 'DELETE 0':
        raise exc.WellNotFoundException()


async def well_get(uuid: UUID, return_trajectory: bool = False) -> dict:
    conn = await make_apg_connection()
    columns: str = 'name, head, md, x, y, z' if return_trajectory else 'name, head'
    
    # elapsed about 300ms (version 1)
    # elapsed about 730ms (version 2)
    query = await conn.fetch(
        f'SELECT {columns} FROM well {'JOIN trajectory ON fk_well_id = $1' if return_trajectory else ''} WHERE well.pk_id = $1',
        uuid
    )
    await conn.close()

    if query is None:
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
