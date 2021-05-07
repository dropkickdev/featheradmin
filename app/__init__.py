from .cache import *
from .exceptions import *

from icecream.icecream import IceCreamDebugger
from app.settings import settings as s



# Icecream
ic = IceCreamDebugger()
ic.enabled = s.DEBUG






