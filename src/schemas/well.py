"""
Содержит набор схем для различных операций с данными о скважинах.

"""

from pydantic import BaseModel, Field, UUID4, computed_field
from typing import Any


class WellSchema(BaseModel):
    method: str = Field(default='well.method')
    params: Any


class WellCreateSchema(WellSchema):
    """
    Тело запроса для создания скважины.

    Параметры:

    name: имя скважины;

    head: координаты устья скважины (x, y);

    MD: список из уровней глубины;

    X, Y, Z: три отдельных списка с координатами точек, представляющих
    саму скважину.

    Аргументы "MD", "X", "Y" и "Z" являются списками из чисел с
    плавающей точкой.
    То есть, элементы X[n], Y[n] и Z[n] представляют координаты
    скважины на глубине MD[n].

    Поэтому аргументы "MD", "X", "Y" и "Z" должны быть одинаковой
    длины!

    """

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
    """
    Тело запроса для удаления скважины.

    Параметры:

    uuid: идентификатор скважины, которую вы хотите удалить.

    """

    class WellRemoveParamsSchema(BaseModel):
        uuid: UUID4 = Field()
    
    params: WellRemoveParamsSchema


class WellGetSchema(WellSchema):
    """
    Тело запроса для получения данных о скважине.

    Параметры:

    uuid: идентификатор скважины;

    return_trajectory: при значении true вместе с основной информацией
    возвращает координаты точек вместе с "MD".
    
    """
    
    class WellGetParamsSchema(BaseModel):
        uuid: UUID4 = Field()
        return_trajectory: bool = Field(default=False)
    
    params: WellGetParamsSchema


class WellAtSchema(WellSchema):
    """
    Тело запроса для получения координат скважины на определенной
    глубине.

    Параметры:

    uuid: идентификатор скважины;

    MD: уровень глубины скважины.

    """
    
    class WellAtParamsSchema(BaseModel):
        uuid: UUID4 = Field()
        MD: float = Field()
    
    params: WellAtParamsSchema


class WellOutputSchema(BaseModel):
    """
    Является основным форматом ответа API.

    Поля:

    data: содержит полученные данные;

    error: содержит информацию об ошибке (имеет значение null, когда
    запрос успешен).

    """

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
