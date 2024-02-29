from pydantic import BaseModel, Field, UUID4
from typing import Any, Sequence


class WellModel(BaseModel):
    method: str
    params: Any


class WellCreateRequest(WellModel):
    class WellCreateParams(BaseModel):
        name: str
        head: tuple[float, float] = Field(default=(0.0, 0.0), min_length=2, max_length=2)
        MD: Sequence = Field(default=[0.0, 0.0], min_length=1)
        X: Sequence = Field(default=[0.0, 0.0], min_length=1)
        Y: Sequence = Field(default=[0.0, 0.0], min_length=1)
        Z: Sequence = Field(default=[0.0, 0.0], min_length=1)
    
    params: WellCreateParams


class WellRemoveRequest(WellModel):
    class WellRemoveParams(BaseModel):
        uuid: UUID4
    
    params: WellRemoveParams

class WellGetRequest(WellModel):
    class WellGetParams(BaseModel):
        uuid: UUID4
        return_trajectory: bool
    
    params: WellGetParams


class WellAtRequest(WellModel):
    class WellGetParams(BaseModel):
        uuid: UUID4
        MD: float
    
    params: WellGetParams
