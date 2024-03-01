import numpy as np
from fastapi import APIRouter

from schemas.well import (
    WellCreateSchema,
    WellRemoveSchema,
    WellGetSchema,
    WellAtSchema,
    WellOutputSchema
)
import services.well as well_services
import services.exceptions as exc


router: APIRouter = APIRouter(
    prefix='/api',
    tags=['Well']
)


@router.post('/well.create')
async def create(well: WellCreateSchema) -> WellOutputSchema:
    output: WellOutputSchema = WellOutputSchema(data=None, error=None)

    try:
        created_well_uuid = await well_services.well_create(
            well.params.name,
            np.float32(well.params.head),
            np.array(well.params.MD, dtype=np.float32),
            np.array(well.params.X, dtype=np.float32),
            np.array(well.params.Y, dtype=np.float32),
            np.array(well.params.Z, dtype=np.float32)
        )
    except exc.WellAlreadyExistsException:
        output.error = 'Well already exists!'
    except exc.ArrayDifferentSizesException:
        output.error = 'Sizes of MD, X, Y and Z must be equal!'
    except exc.InconsistentHeadAndFirstNodeException:
        output.error = 'Well head and trajectory are inconsistent!'
    else:
        output.data = { 'uuid': str(created_well_uuid) }

    return output


@router.post('/well.remove')
async def remove(well: WellRemoveSchema) -> WellOutputSchema:
    output: WellOutputSchema = WellOutputSchema(data=None, error=None)

    try:
        await well_services.well_remove(well.params.uuid)
    except exc.WellNotFoundException:
        output.error = 'Well not found!'
    
    return output


@router.post('/well.get')
async def get(well: WellGetSchema) -> WellOutputSchema:
    output: WellOutputSchema = WellOutputSchema(data=None, error=None)

    try:
        queried_well = await well_services.well_get(
            well.params.uuid,
            well.params.return_trajectory
        )
    except exc.WellNotFoundException:
        output.error = 'Well not found!'
    else:
        output.data = queried_well

    return output


@router.post('/well.at')
async def at(well: WellAtSchema) -> WellOutputSchema:
    output: WellOutputSchema = WellOutputSchema(data=None, error=None)
    
    try:
        coordinates: tuple[float, float, float] = await well_services.well_at(
            well.params.uuid,
            well.params.MD
        )
    except exc.WellNotFoundException:
        output.error = 'Well not found!'
    else:
        output.data = {
            'X': coordinates[0],
            'Y': coordinates[1],
            'Z': coordinates[2]
        }
    
    return output
