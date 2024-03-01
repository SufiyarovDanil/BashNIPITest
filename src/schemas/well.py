from pydantic import BaseModel, Field, UUID4, computed_field
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

    def __init__(self, data: dict[str, Any] | None = None, error: dict[str, str] | None = None):
        super().__init__(data=data, error=error)
        self.data = data
        self.error = error
    
    @computed_field
    @property
    def error(self) -> dict[str, str] | None:
        return self._error
    
    @error.setter
    def error(self, value: str | None) -> None:
        self._error = value if value is None else { 'message': value }
