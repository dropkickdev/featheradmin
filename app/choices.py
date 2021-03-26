from enum import Enum, IntEnum


class Gender(str, Enum):
    male = 'male'
    female = 'female'
    none = ''
    

class CivilStatus(Enum):
    single = 'single'
    married = 'married'
    livein = 'livein'
    none = ''
