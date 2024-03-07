from typing import Any
from uuid import UUID

import asyncpg as apg
import numpy as np
import asyncpg.exceptions as apg_exc

import services.exceptions as exc
from database import db_instance


async def well_create(
        well_name: str,
        well_head: tuple[float, float],
        md: list[float],
        x: list[float],
        y: list[float],
        z: list[float]) -> UUID:
    if not (len(md) == len(x) == len(y) == len(z)):
        raise exc.ArrayDifferentSizesException()

    if well_head[0] != x[0] or well_head[1] != y[0]:
        raise exc.InconsistentHeadAndFirstNodeException()

    md_array: np.ndarray[Any, np.dtype[np.float64]] = np.asarray(
        md, dtype=np.float64
    )
    x_array: np.ndarray[Any, np.dtype[np.float64]] = np.asarray(
        x, dtype=np.float64
    )
    y_array: np.ndarray[Any, np.dtype[np.float64]] = np.asarray(
        y, dtype=np.float64
    )
    z_array: np.ndarray[Any, np.dtype[np.float64]] = np.asarray(
        z, dtype=np.float64
    )

    try:
        well_id: UUID = await db_instance.fetch_val(
            '''SELECT insert_well(
                $1,
                $2,
                $3::DOUBLE PRECISION[],
                $4::DOUBLE PRECISION[],
                $5::DOUBLE PRECISION[],
                $6::DOUBLE PRECISION[])''',
            well_name,
            well_head,
            md_array,
            x_array,
            y_array,
            z_array
        )
    except apg_exc.UniqueViolationError:
        raise exc.WellAlreadyExistsException()

    return well_id


async def well_remove(uuid: UUID) -> None:
    is_deleted: bool = await db_instance.fetch_val(
        'SELECT * FROM delete_well($1)',
        uuid
    )

    if not is_deleted:
        raise exc.WellNotFoundException()


async def well_get(uuid: UUID,
                   return_trajectory: bool = False) -> dict[str, Any]:
    columns: str = (
        'name, head, md as "MD", x as "X", y as "Y", z as "Z"'
        if return_trajectory else 'name, head'
    )

    try:
        query: apg.Record | None = await db_instance.fetch_row(
            f'SELECT {columns} FROM well_{uuid.hex}'
        )
    except apg_exc.UndefinedTableError:
        raise exc.WellNotFoundException()

    if not query:
        raise exc.WellNotFoundException()

    return dict(query)


async def well_at(uuid: UUID, md: float) -> tuple[float, float, float]:
    try:
        well_trajectory: apg.Record | None = await db_instance.fetch_row(
            f'SELECT md, x, y, z FROM well_{uuid.hex}'
        )
    except apg_exc.UndefinedTableError:
        raise exc.WellNotFoundException()
    
    if not well_trajectory:
        raise exc.WellNotFoundException()

    md_array: np.ndarray[Any, np.dtype[np.float64]] = np.asarray(
        well_trajectory['md'])

    x: float = float(np.interp(md, md_array, well_trajectory['x']))
    y: float = float(np.interp(md, md_array, well_trajectory['y']))
    z: float = float(np.interp(md, md_array, well_trajectory['z']))

    return x, y, z
