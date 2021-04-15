from typing import Union
from tortoise.query_utils import Prefetch

from app import ic, red, cache
from app.settings import settings as s


class UserMixin(object):
    pass