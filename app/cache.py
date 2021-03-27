import pickle
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


def makesafe(val):
    if isinstance(val, (list, dict)):
        return repr(val)
    elif isinstance(val, bool):
        return int(val)
    else:
        return str(val)


def prepareuser(user_dict: dict) -> dict:
    """
    Prepare the dict before saving it to redis. Converts data to str or int.
    :param user_dict:   User data taken from user.to_dict()
    :return:            dict
    """
    d = {}
    for k, v in user_dict.items():
        d[k] = makesafe(v)
    return d


def restoreuser(user_dict: dict) -> dict:
    """
    Restores the user to its native python data types
    :param user_dict:   Dict from red.get()
    :return:            dict
    """
    d = user_dict.copy()
    d['id'] = UUID4(d.pop('id'))
    for k, v in d.items():
        if k in ['groups', 'permissions']:
            d[k] = literal_eval(d.get(k))
        elif k in ['is_active', 'is_superuser', 'is_verified']:
            d[k] = bool(d.get(k))
        elif k in ['options']:
            d[k] = dict(literal_eval(d.get(k)))
    return d