from enum import Enum


class GenderChoices(Enum):
    male = 'male'
    female = 'female'
    none = ''
    

class CivilStatChoices(Enum):
    single = 'single'
    married = 'married'
    livein = 'livein'
    none = ''


class PermChoices(Enum):
    user = 'user'
    group = 'group'
    
