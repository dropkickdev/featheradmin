from typing import Union
from ast import literal_eval
from limeutils import Red

from app.settings import settings as s


# Redis
red = Red(**s.CACHE_CONFIG.get('default'))