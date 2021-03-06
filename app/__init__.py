from redis import Redis

from icecream.icecream import IceCreamDebugger
from app.settings import settings as s



"""
DATA TO CACHE:
current_user()
Groups
Permissions of each group
"""

# Redis
r = Redis()

# Icecream
ic = IceCreamDebugger()
ic.enabled = s.DEBUG




