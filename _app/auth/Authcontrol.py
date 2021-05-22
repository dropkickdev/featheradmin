import secrets, pytz
from gettext import gettext as _
from datetime import datetime, timedelta

from app.settings import settings as s
from .models import UserMod, TokenMod


    



class Authutils:
    
    
    @staticmethod
    def _time_difference(expires: datetime, now: datetime = None):
        """Get the diff between 2 dates"""
        now = now or datetime.now(tz=pytz.UTC)
        diff = expires - now
        return {
            'days': diff.days,
            'hours': int(diff.total_seconds()) // 3600,
            'minutes': int(diff.total_seconds()) // 60,
            'seconds': int(diff.total_seconds()),
        }
    
    @classmethod
    def expires(cls, expires: datetime, units: str = 'minutes'):
        diff = cls._time_difference(expires)
        return diff[units]