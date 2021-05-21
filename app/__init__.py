# import logging, pytz
# from datetime import datetime
# from fastapi.logger import logger
#
# from .cache import *
from .exceptions import *
from .settings import *

from icecream.icecream import IceCreamDebugger
from app.settings import settings as s



# Icecream
ic = IceCreamDebugger()
ic.enabled = s.DEBUG

# This works, just commenting out for now. Put it back later.
# Logger
# tz = pytz.timezone('Asia/Manila')
# now = datetime.now(tz=tz).strftime('%Y-%m-%d')
# formatting = '%(asctime)s %(levelname)s %(filename)s %(funcName)s() %(lineno)d: %(message)s'
#
# handler = logging.FileHandler(f'logs/{now}.log')
# handler.setFormatter(logging.Formatter(formatting))
# logger.addHandler(handler)




