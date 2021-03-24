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


def prepareuser(user_dict: dict):
    """
    Prepare the dict before saving it to redis. Converts data to str or int.
    :param user_dict:   User data taken from user.to_dict()
    :return:            dict
    """
    for k, v in user_dict.items():
        if k in ['groups', 'permissions', 'options']:
            v = repr(v)
        elif k == 'id':
            v = str(v)
        elif isinstance(v, bool):
            v = int(v)
        user_dict[k] = v
    return user_dict


def restoreuser(user_dict: dict):
    """
    Restores the user to its native python data types
    :param user_dict:   Dict from red.get()
    :return:
    """
    user_dict['id'] = UUID4(user_dict.get('id'))
    for k, v in user_dict.items():
        if k in ['groups', 'permissions']:
            user_dict[k] = set(literal_eval(user_dict.get(k)))
        elif k in ['is_active', 'is_superuser', 'is_verified']:
            user_dict[k] = bool(user_dict.get(k))
        elif k in ['options']:
            user_dict[k] = dict(literal_eval(user_dict.get(k)))
    return user_dict