import pytest, json, asyncio
from collections import Counter
from tortoise import Tortoise

from main import get_app
from app import ic, red
from app.settings import settings as s
from app.settings.db import DATABASE
from app.auth import Permission, Group, UserMod
from app.settings.db import DATABASE_MODELS, DATABASE_URL



admin = ['user.create', 'user.delete', 'user.hard_delete', 'auth.ban', 'auth.unban', 'auth.reset_password_counter']
staff = ['auth.ban', 'auth.unban', 'auth.reset_password_counter']
noadd = ['foo.read', 'foo.update', 'foo.delete', 'foo.hard_delete', 'user.create', 'user.delete', 'user.hard_delete']

param = [
    ('AdminGroup', admin, 'db'), ('StaffGroup', staff, 'db'), ('NoaddGroup', noadd, 'db'),
    ('AdminGroup', admin, 'cache'), ('StaffGroup', staff, 'cache'), ('NoaddGroup', noadd, 'cache'),
]
@pytest.mark.parametrize('name, out, cat', param)
# @pytest.mark.focus
@pytest.mark.asyncio
async def test_group_get_permissions(client, headers, name, out, cat):
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


@pytest.mark.focus
@pytest.mark.asyncio
async def test_permissions_get_groups(db):
    param = [
        ('user.create', ['AdminGroup', 'NoaddGroup']),
        ('page.create', ['DataGroup'])
    ]
    for i in param:
        perm, out = i
        groups = await Permission.get_groups(perm)
        assert Counter(groups) == Counter(out)
    