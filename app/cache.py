from limeutils import Red

from app.settings import settings as s



"""
DATA TO CACHE:
current_user()
Groups
Permissions of each group
"""

# Redis
red = Red(**s.CACHE_CONFIG.get('default'))