# from redis import Redis
# import redis
from limeutils import Redis

from icecream.icecream import IceCreamDebugger
from app.settings import settings as s



# Icecream
ic = IceCreamDebugger()
ic.enabled = s.DEBUG


"""
DATA TO CACHE:
current_user()
Groups
Permissions of each group
"""
# Redis
redconn = Redis(**s.CACHE_CONFIG.get('default'))



