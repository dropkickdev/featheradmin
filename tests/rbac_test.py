import pytest, json
from collections import Counter

from app import ic, red
from app.settings import settings as s
from app.auth import Permission, Group, UserMod



admin = ['user.create', 'user.delete', 'user.hard_delete', 'auth.ban', 'auth.unban', 'auth.reset_password_counter']
staff = ['auth.ban', 'auth.unban', 'auth.reset_password_counter']
noadd = ['foo.read', 'foo.update', 'foo.delete', 'foo.hard_delete']

param = [
    ('AdminGroup', admin, 'db'), ('StaffGroup', staff, 'db'), ('NoaddGroup', noadd, 'db'),
    ('AdminGroup', admin, 'cache'), ('StaffGroup', staff, 'cache'), ('NoaddGroup', noadd, 'cache'),
]
@pytest.mark.parametrize('name, out, cat', param)
# @pytest.mark.focus
@pytest.mark.asyncio
async def test_get_permissions(client, headers, name, out, cat):
    keyname = s.CACHE_GROUPNAME.format(name)
    perms = []
    if cat == 'cache':
        assert red.exists(keyname)
        perms = await Group.get_permissions(name)
    elif cat == 'db':
        red.delete(keyname)
        perms = await Group.get_permissions(name)
        assert red.exists(keyname)
    assert Counter(perms) == Counter(out)
    