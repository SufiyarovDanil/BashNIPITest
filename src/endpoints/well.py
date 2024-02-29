import numpy as np
import time
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from schemas.well import (
    WellCreateRequest,
    WellRemoveRequest,
    WellGetRequest,
    WellAtRequest
)
import services.well as well_services
import services.exceptions as exc


router: APIRouter = APIRouter(
    prefix='/api',
    tags=['Well']
)


@router.post('/well.create')
async def create(well: WellCreateRequest) -> JSONResponse:
    result: dict = {
        'data': None,
        'error': None
    }

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
        result['error'] = { 'message': 'Well already exists!' }
    except exc.ArrayDifferentSizesException:
        result['error'] = { 'message': 'Sizes of MD, X, Y and Z must be equal!' }
    except exc.InconsistentHeadAndFirstNodeException:
        result['error'] = { 'message': 'Well head and trajectory are inconsistent!' }
    else:
        result['data'] = { 'uuid': str(created_well_uuid) }

    return JSONResponse(result)


@router.post('/well.remove')
async def remove(well: WellRemoveRequest) -> JSONResponse:
    result: dict = {
        'data': None,
        'error': None
    }

    try:
        await well_services.well_remove(well.params.uuid)
    except exc.WellNotFoundException:
        result['error'] = { 'message': 'Well not found!' }
    
    return JSONResponse(result)


@router.post('/well.get')
async def get(well: WellGetRequest) -> JSONResponse:
    result: dict = {
        'data': None,
        'error': None
    }

    try:
        queried_well = await well_services.well_get(
            well.params.uuid,
            well.params.return_trajectory
        )
    except exc.WellNotFoundException:
        result['error'] = { 'message': 'Well not found!' }
    else:
        result['data'] = queried_well

    return JSONResponse(result)


@router.post('/well.at')
async def at(well: WellAtRequest) -> JSONResponse:
    result: dict = {
        'data': None,
        'error': None
    }
    
    try:
        coordinates: tuple[float, float, float] = await well_services.well_at(
            well.params.uuid,
            well.params.MD
        )
    except exc.WellNotFoundException:
        result['error'] = { 'message': 'Well not found!' }
    else:
        result['data'] = {
            'X': coordinates[0],
            'Y': coordinates[1],
            'Z': coordinates[2]
        }
    
    return JSONResponse(result)
