from typing import Any
from uuid import UUID

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
        created_well_uuid: UUID = await well_services.well_create(
            well.params.name,
            well.params.head,
            well.params.MD,
            well.params.X,
            well.params.Y,
            well.params.Z
        )
    except exc.WellAlreadyExistsException as e:
        output.error = str(e)
    except exc.ArrayDifferentSizesException as e:
        output.error = str(e)
    except exc.InconsistentHeadAndFirstNodeException as e:
        output.error = str(e)
    else:
        output.data = {'uuid': str(created_well_uuid)}

    return output


@router.post('/well.remove')
async def remove(well: WellRemoveSchema) -> WellOutputSchema:
    output: WellOutputSchema = WellOutputSchema()

    try:
        await well_services.well_remove(well.params.uuid)
    except exc.WellNotFoundException as e:
        output.error = str(e)
    
    return output


@router.post('/well.get')
async def get(well: WellGetSchema) -> WellOutputSchema:
    output: WellOutputSchema = WellOutputSchema(data=None, error=None)

    try:
        queried_well: dict[str, Any] = await well_services.well_get(
            well.params.uuid,
            well.params.return_trajectory
        )
    except exc.WellNotFoundException as e:
        output.error = str(e)
    else:
        output.data = queried_well

    return output


@router.post('/well.at')
async def at(well: WellAtSchema) -> WellOutputSchema:
    output: WellOutputSchema = WellOutputSchema()
    
    try:
        coordinates: tuple[float, float, float] = await well_services.well_at(
            well.params.uuid,
            well.params.MD
        )
    except exc.WellNotFoundException as e:
        output.error = str(e)
    else:
        output.data = {
            'X': coordinates[0],
            'Y': coordinates[1],
            'Z': coordinates[2]
        }
    
    return output
