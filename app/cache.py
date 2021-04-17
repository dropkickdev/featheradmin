import pickle
from typing import Union
from ast import literal_eval
from limeutils import Red
from pydantic import UUID4

from app.settings import settings as s


"""
DATA TO CACHE:
current_user()
Groups
Permissions of each group
"""

# Redis
red = Red(**s.CACHE_CONFIG.get('default'))


def makesafe(val) -> Union[str, int]:
    """
    Moke lists, sets, and bool safe as a string. Used for hash values.
    This literally adds quotes to make it safe for saving as a hash value in redis.
    :param val: Item to make into a string
    :return:    str
    """
    if isinstance(val, (list, dict)):
        return repr(val)
    elif isinstance(val, bool):
        return int(val)
    else:
        return str(val)

def prepareuser_dict(user_dict: dict) -> dict:
    """
    Prepare the dict before saving it to redis. Converts data to str or int.
    :param user_dict:   User data taken from user.to_dict()
    :return:            dict
    """
    d = {}
    for k, v in user_dict.items():
        d[k] = makesafe(v)
    return d

def restoreuser_dict(user_dict: dict) -> dict:
    """
    Restores the user to its native python data types
    :param user_dict:   Dict from red.get()
    :return:            dict
    """
    d = user_dict.copy()
    for k, v in d.items():
        if k in ['groups', 'permissions']:
            d[k] = literal_eval(d.get(k))
        elif k in ['is_active', 'is_superuser', 'is_verified']:
            d[k] = bool(d.get(k))
        elif k in ['options']:
            d[k] = dict(literal_eval(d.get(k)))
    return d