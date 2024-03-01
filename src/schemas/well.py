from pydantic import BaseModel, Field, UUID4
from typing import Any, Sequence


class WellSchema(BaseModel):
    method: str
    params: Any


class WellCreateSchema(WellSchema):
    class WellCreateParamsSchema(BaseModel):
        name: str
        head: tuple[float, float] = Field(default=(0.0, 0.0), min_length=2, max_length=2)
        MD: Sequence = Field(default=[0.0, 0.0], min_length=1)
        X: Sequence = Field(default=[0.0, 0.0], min_length=1)
        Y: Sequence = Field(default=[0.0, 0.0], min_length=1)
        Z: Sequence = Field(default=[0.0, 0.0], min_length=1)
    
    params: WellCreateParamsSchema


class WellRemoveSchema(WellSchema):
    class WellRemoveParamsSchema(BaseModel):
        uuid: UUID4
    
    params: WellRemoveParamsSchema

class WellGetSchema(WellSchema):
    class WellGetParamsSchema(BaseModel):
        uuid: UUID4
        return_trajectory: bool
    
    params: WellGetParamsSchema


class WellAtSchema(WellSchema):
    class WellGetParamsSchema(BaseModel):
        uuid: UUID4
        MD: float
    
    params: WellGetParamsSchema


class WellOutputSchema(BaseModel):
    data: dict[str, Any] | None = Field(default=None)
    # error: dict[str, str] | None = Field(default=None)
    @property
    def error(self) -> dict[str, str] | None:
        return None
    
    @error.setter
    def error(self, message: str | None) -> None:
        self.error = { 'message': message }
