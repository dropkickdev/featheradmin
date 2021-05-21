import secrets, pytz
from gettext import gettext as _
from datetime import datetime, timedelta

from app.settings import settings as s
from .models import UserMod, TokenMod


class Authcontrol:
    @staticmethod
    def refresh_cookie(name: str, token: dict, **kwargs):
        if token['expires'] <= datetime.now(tz=pytz.UTC):
            raise ValueError(_('Cookie expires date must be greater than the date now'))

        expires = token['expires'] - datetime.now(tz=pytz.UTC)
        cookie_data = {
            'key': name,
            'value': token['value'],
            'httponly': True,
            'expires': expires.seconds,
            'path': '/',
            **kwargs,
        }
        if not s.DEBUG:
            cookie_data.update({
                'secure': True
            })
        return cookie_data


    # TODO: Converted this to an object method instead of a class method so updates are needed
    @staticmethod
    async def create_refresh_token(user) -> dict:
        """
        Create and save a new refresh token
        :param user Pydantic model for the user
        """
        user = await UserMod.get(pk=user.id).only('id')
        refresh_token = Authutils.generate_refresh_token()
        expires = datetime.now(tz=pytz.UTC) + timedelta(seconds=s.REFRESH_TOKEN_EXPIRE)

        await TokenMod.create(token=refresh_token, expires=expires, author=user)
        return {
            'value': refresh_token,
            'expires': expires,
        }


    # TODO: Converted this to an object method instead of a class method so updates are needed
    @staticmethod
    async def update_refresh_token(user, token: TokenMod = None) -> dict:
        """
        Update the refresh token of the user
        :param user     Pydantic model for the user
        :param token    Use an existing TokenMod instance if there is one and save a query
        """
        refresh_token = Authutils.generate_refresh_token()
        expires = datetime.now(tz=pytz.UTC) + timedelta(seconds=s.REFRESH_TOKEN_EXPIRE)
        
        if not token:
            token = await TokenMod.get(author_id=user.id, is_blacklisted=False) \
                .only('id', 'token', 'expires')
            
        token.token = refresh_token
        token.expires = expires
        await token.save(update_fields=['token', 'expires'])
        return {
            'value': refresh_token,
            'expires': expires,
        }



class Authutils:
    
    @staticmethod
    def generate_refresh_token(nbytes: int = 32):
        return secrets.token_hex(nbytes=nbytes)
    
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