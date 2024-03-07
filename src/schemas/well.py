from uuid import uuid4

from pydantic import BaseModel, Field, UUID4, computed_field
from typing import Any


class WellSchema(BaseModel):
    method: str
    params: Any


class WellCreateSchema(WellSchema):
    class WellCreateParamsSchema(BaseModel):
        name: str = Field(default='well_name', min_length=1)
        head: tuple[float, float] = Field(default=(0.0, 0.0),
                                          min_length=2, max_length=2)
        MD: list[float] = Field(default=[0.0, 0.0], min_length=1)
        X: list[float] = Field(default=[0.0, 0.0], min_length=1)
        Y: list[float] = Field(default=[0.0, 0.0], min_length=1)
        Z: list[float] = Field(default=[0.0, 0.0], min_length=1)
    
    params: WellCreateParamsSchema


class WellRemoveSchema(WellSchema):
    class WellRemoveParamsSchema(BaseModel):
        uuid: UUID4 = Field(default=uuid4())
    
    params: WellRemoveParamsSchema


class WellGetSchema(WellSchema):
    class WellGetParamsSchema(BaseModel):
        uuid: UUID4 = Field(default=uuid4())
        return_trajectory: bool = Field(default=False)
    
    params: WellGetParamsSchema


class WellAtSchema(WellSchema):
    class WellGetParamsSchema(BaseModel):
        uuid: UUID4 = Field(default=uuid4())
        MD: float = Field()
    
    params: WellGetParamsSchema


class WellOutputSchema(BaseModel):
    data: dict[str, Any] | None = Field(default=None)

    def __init__(self,
                 data: dict[str, Any] | None = None,
                 error: dict[str, str] | None = None):
        super().__init__(data=data, error=error)
        self.data = data
        self.error = error
    
    @computed_field
    @property
    def error(self) -> dict[str, str] | None:
        return self._error
    
    @error.setter
    def error(self, value: str | None) -> None:
        self._error = value if value is None else {'message': value}
