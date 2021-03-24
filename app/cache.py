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


def prepare(user_dict: dict):
    for k, v in user_dict.items():
        # if k in ['groups', 'permissions', 'options']:
        #     continue
        if k in ['groups', 'permissions', 'options']:
            v = repr(v)
        elif k == 'id':
            v = str(v)
        elif isinstance(v, bool):
            v = int(v)
        user_dict[k] = v
    return user_dict


def restore(user_dict: dict):
    user_dict['id'] = UUID4(user_dict.get('id'))
    for k, v in user_dict.items():
        if k in ['groups', 'permissions']:
            user_dict[k] = set(literal_eval(user_dict.get(k)))
        elif k in ['is_active', 'is_superuser', 'is_verified']:
            user_dict[k] = bool(user_dict.get(k))
        elif k in ['options']:
            user_dict[k] = dict(literal_eval(user_dict.get(k)))
    return user_dict