from enum import Enum, IntEnum


class Gender(str, Enum):
    male = 'male'
    female = 'female'
    none = ''