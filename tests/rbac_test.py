import pytest
from collections import Counter
from limeutils import listify

from app import ic, red
from app.settings import settings as s
from app.auth import Permission, Group


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


param = [
    ('user.create', ['AdminGroup', 'NoaddGroup']),
    (['user.create'], ['AdminGroup', 'NoaddGroup']),
    ('page.create', ['DataGroup']),
    (['user.create', 'page.create'], ['AdminGroup', 'NoaddGroup', 'DataGroup']),
    ([], [])
]
@pytest.mark.parametrize('perm, out', param)
# @pytest.mark.focus
def test_permission_get_groups(loop, perm, out):
    async def ab():
        perms = listify(perm)
        groups = await Permission.get_groups(*perms)
        assert Counter(groups) == Counter(out)
    loop.run_until_complete(ab())


param = [
    ('user.create', 'AdminGroup', True),
    ('user.create', 'NoaddGroup', True),
    ('page.create', 'DataGroup', True),
    ('page.create', 'NoaddGroup', False),
    ('page.create', 'abc', False),
    ('', 'abc', False),
    ('page.create', '', False),
]
# @pytest.mark.parametrize('perm, group, out', param)
# @pytest.mark.focus
# def test_is_group(loop, perm, group, out):
#     async def ab():
#         assert await Permission.is_group(perm, group) == out
#     loop.run_until_complete(ab())


# # @pytest.mark.focus
# def test_abc(loop, tempdb):
#     from app.auth import Option
#
#     async def ab():
#         await tempdb()
#         await Option.create(name='foo', value='bar')
#         opt = await Option.all()
#         ic(opt)
#
#     loop.run_until_complete(ab())