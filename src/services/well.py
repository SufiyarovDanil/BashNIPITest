import numpy as np
import asyncpg.exceptions as apg_exc

from . import exceptions as exc
from database import make_apg_connection


async def well_create(
    well_name: str,
    well_head: tuple[float, float],
    md: np.ndarray,
    x: np.ndarray,
    y: np.ndarray,
    z: np.ndarray
) -> str:
    if not (md.size == x.size == y.size == z.size):
        raise exc.ArrayDifferentSizesException()
    if not (well_head[0] == x[0] and well_head[1] == y[0]):
        raise exc.InconsistentHeadAndFirstNodeException()
    
    trajectory: np.ndarray = np.array([(i[0], i[1], i[2]) for i in np.column_stack((x, y, z))], dtype='f,f,f')
    conn = await make_apg_connection()

    try:
        await conn.execute(
            'INSERT INTO well(pk_id, name, head, measured_depth, trajectory) VALUES (gen_random_uuid(), $1, $2, $3, $4)',
            well_name,
            well_head,
            md,
            trajectory
        )
    except apg_exc.UniqueViolationError:
        raise exc.WellAlreadyExistsException()
    
    query = await conn.fetchrow('SELECT pk_id FROM well WHERE name = $1', well_name)
    await conn.close()

    return str(query['pk_id'])


async def well_remove(uuid: str) -> None:
    conn = await make_apg_connection()
    stmt = await conn.execute(
        'DELETE FROM well WHERE pk_id = $1',
        uuid
    )
    await conn.close()

    if stmt == 'DELETE 0':
        raise exc.WellNotFoundException()


async def well_get(uuid: str, return_trajectory: bool = False) -> dict:
    conn = await make_apg_connection()
    columns: str = 'name, head, measured_depth, trajectory' if return_trajectory else 'name, head'
    
    # elapsed about 300ms
    query = await conn.fetchrow(
        f'SELECT {columns} FROM well WHERE pk_id = $1',
        uuid
    )
    await conn.close()

    if query is None:
        raise exc.WellNotFoundException()
    
    result: dict = {
        'name': query['name'],
        'head': (query['head'].x, query['head'].y)
    }

    if return_trajectory:
        transparent_trajectory: np.ndarray = np.array([[i['x'], i['y'], i['z']] for i in query['trajectory']]).T
        result['MD'] = query['measured_depth']
        result['X'] = transparent_trajectory[0]
        result['Y'] = transparent_trajectory[1]
        result['Z'] = transparent_trajectory[2]

    return result


async def well_at(uuid: str, md: float) -> tuple[float, float, float]:
    well: dict = await well_get(uuid, True)

    x: float = np.interp([md], well['MD'], well['X'])[0]
    y: float = np.interp([md], well['MD'], well['Y'])[0]
    z: float = np.interp([md], well['MD'], well['Z'])[0]

    return (x, y, z)
