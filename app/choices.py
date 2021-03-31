from enum import Enum, IntEnum


class Gender(Enum):
    male = 'male'
    female = 'female'
    none = ''
    

class CivilStatus(Enum):
    single = 'single'
    married = 'married'
    livein = 'livein'
    none = ''


class PermChoices(Enum):
    user = 'user'
    group = 'group'
    
