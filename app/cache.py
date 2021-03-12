from limeutils import Redis

from app.settings import settings as s



"""
DATA TO CACHE:
current_user()
Groups
Permissions of each group
"""

# Redis
redconn = Redis(**s.CACHE_CONFIG.get('default'))