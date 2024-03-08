"""
Кастомные исключения, которые бросаются в функциях сервиса well.

"""

class WellNotFoundException(Exception):
    def __init__(self):
        super().__init__('Well not found!')


class WellAlreadyExistsException(Exception):
    def __init__(self):
        super().__init__('Well already exists!')


class InconsistentHeadAndFirstNodeException(Exception):
    def __init__(self):
        super().__init__('Well head and trajectory are inconsistent!')


class ArrayDifferentSizesException(Exception):
    def __init__(self):
        super().__init__('Sizes of MD, X, Y and Z must be equal!')
