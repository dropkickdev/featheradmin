import pytest, json
from collections import Counter
from pydantic import EmailStr
from uuid import UUID
from limeutils import listify

from app import ic
from app.auth import current_user, userdb
from app.cache import red
from app import cache
from app.settings import settings as s
from .auth_test import VERIFIED_USER_DEMO, VERIFIED_EMAIL_DEMO, UNVERIFIED_EMAIL_DEMO
from app.auth.models import UserMod, UserDBComplete, UserDB, UserPermissions, Permission
from .data import accountperms, noaddperms, contentperms, staffperms

param = [
    ('id', str), ('email', str), ('is_active', bool), ('is_verified', bool),
    ('is_superuser', bool), ('username', str), ('timezone', str),
    ('groups', list), ('options', dict),
    # ('permissions', list)
]
@pytest.mark.parametrize('attr, tp', param)
@pytest.mark.userdata
def test_current_user_data(loop, client, passwd, headers, attr, tp):
    res = client.post('/test/dev_user_data', headers=headers)
    data = res.json()
    # ic(data)
    assert isinstance(data.get(attr), tp)


param = [
    ('id', str), ('email', str), ('is_active', bool), ('is_verified', bool), ('is_superuser', bool),
    ('username', str), ('timezone', str), ('groups', list), ('options', dict),
]
@pytest.mark.parametrize('attr, tp', param)
# @pytest.mark.focus
def test_get_and_cache(tempdb, loop, attr, tp):
    async def ab():
        # await tempdb()
        return await UserMod.get_and_cache(VERIFIED_USER_DEMO)
    
    user = loop.run_until_complete(ab())
    assert isinstance(getattr(user, attr), tp)
    
    if attr == 'id':
        assert user.id == VERIFIED_USER_DEMO
    elif attr == 'groups':
        assert Counter(user.groups) == Counter(s.USER_GROUPS)
    
    # Last
    if attr == param[-1][0]:
        user_dict = user.dict()
        keys = user_dict.keys()
        assert set(userdb.select_fields).issubset(set(keys))

# @pytest.mark.focus
def test_get_groups(tempdb, loop):
    async def get_user():
        await tempdb()
        return await UserMod.get(email=VERIFIED_EMAIL_DEMO).only('id')
    
    async def ab(user):
        partialkey = s.CACHE_USERNAME.format(user.id)

        red.delete(partialkey)
        groups, source = await user.get_groups(debug=True)
        assert groups == s.USER_GROUPS
        assert source == 'QUERY'
        
        groups, source = await user.get_groups(debug=True)
        assert groups == s.USER_GROUPS
        assert source == 'CACHE'
        
        groups, source = await user.get_groups(debug=True)
        assert groups == s.USER_GROUPS
        assert source == 'CACHE'

        red.delete(partialkey)
        groups, source = await user.get_groups(debug=True)
        assert groups == s.USER_GROUPS
        assert source == 'QUERY'

        groups, source = await user.get_groups(debug=True)
        assert groups == s.USER_GROUPS
        assert source == 'CACHE'

        data = await user.get_groups()
        assert isinstance(data, list)
        assert data == s.USER_GROUPS

    user = loop.run_until_complete(get_user())
    loop.run_until_complete(ab(user))
    
# @pytest.mark.focus
def test_has_group(tempdb, loop):
    async def ab():
        await tempdb()
        user = await UserMod.get(email=VERIFIED_EMAIL_DEMO).only('id')
        assert await user.has_group(s.USER_GROUPS[0])
        assert await user.has_group(s.USER_GROUPS[1])
        assert await user.has_group(s.USER_GROUPS[0], s.USER_GROUPS[1])
        assert not await user.has_group('NoaddGroup')
        assert not await user.has_group(s.USER_GROUPS[0], 'NoaddGroup')
        assert not await user.has_group(s.USER_GROUPS[0], s.USER_GROUPS[1], 'NoaddGroup')
    loop.run_until_complete(ab())

param = [
    ('StaffGroup', s.USER_GROUPS + ['StaffGroup']),
    (['StaffGroup'], s.USER_GROUPS + ['StaffGroup']),
    (['StaffGroup', 'NoaddGroup'], s.USER_GROUPS + ['StaffGroup', 'NoaddGroup']),
    (['StaffGroup', 'xxx'], s.USER_GROUPS + ['StaffGroup']),
    (['StaffGroup', None], s.USER_GROUPS + ['StaffGroup']),
    (['StaffGroup', ''], s.USER_GROUPS + ['StaffGroup']),
    (['StaffGroup', False], s.USER_GROUPS + ['StaffGroup']),
    (['StaffGroup', True], s.USER_GROUPS + ['StaffGroup']),
    ('', s.USER_GROUPS), (None, s.USER_GROUPS),
    (s.USER_GROUPS, s.USER_GROUPS),
    (['', None, False, True], s.USER_GROUPS),
    (['', None, False, True, 'StaffGroup'], s.USER_GROUPS + ['StaffGroup']),
]
@pytest.mark.parametrize('addgroups, out', param)
# @pytest.mark.focus
def test_add_groups(tempdb, loop, addgroups, out):
    async def ab():
        await tempdb()
        user = await UserMod.get(email=VERIFIED_EMAIL_DEMO).only('id')
        partialkey = s.CACHE_USERNAME.format(user.id)
        await UserMod.get_and_cache(user.id)
        
        groups = await user.get_groups()
        assert Counter(groups) == Counter(s.USER_GROUPS)
        cached_groups = UserDBComplete(**cache.restoreuser_dict(red.get(partialkey))).groups
        assert Counter(groups) == Counter(cached_groups)

        newgroups = await user.add_groups(*listify(addgroups))      # noqa
        if newgroups:
            assert Counter(newgroups) == Counter(out)
        updatedgroups = await user.get_groups()
        if updatedgroups:
            assert Counter(updatedgroups) == Counter(out)
    
        cached_groups = UserDBComplete(**cache.restoreuser_dict(red.get(partialkey))).groups
        if cached_groups:
            assert Counter(cached_groups) == Counter(out)
    loop.run_until_complete(ab())

starterperms = list(set(accountperms + contentperms + ['foo.delete', 'foo.hard_delete']))
param = [
    ('', starterperms), ('xxx', starterperms), (None, starterperms), ([], starterperms),
    (None, starterperms), ('StaffGroup', list(set(starterperms + staffperms))),
    (['StaffGroup', 'xxx'], list(set(starterperms + staffperms))),
    (['StaffGroup', 'NoaddGroup'], list(set(starterperms + staffperms + noaddperms))),
]
@pytest.mark.parametrize('addgroups, out', param)
# @pytest.mark.focus
def test_get_permissions(tempdb, loop, addgroups, out):
    async def ab():
        await tempdb()
        user = await UserMod.get(email=VERIFIED_EMAIL_DEMO).only('id')
        
        perms = await user.get_permissions()
        assert Counter(perms) == Counter(starterperms)
        
        await user.add_groups(*listify(addgroups))
        perms = await user.get_permissions()
        if perms:
            assert Counter(perms) == Counter(out)
    loop.run_until_complete(ab())
        

param = [
    ('account.read', True), (['account.read'], True),
    (['account.read', 'message.create'], True),
    (['account.read', 'message.create', 'profile.read'], True),
    (['account.read', 'message.create', 'foo.read'], False),
    (['account.read', 'message.create', 'foo.delete'], True),
    (['foo.delete', 'foo.hard_delete'], True),
    (['foo.delete', 'foo.hard_delete', 'foo.read'], False),
    (['account.read', 'message.create', ''], True),
    (['account.read', 'message.create', None], True),
    (['account.read', 'message.create', 'foo'], False),
    (['foo.read'], False), ('foo.read', False), (['foo.read', 'account.read'], False),
    ([], False), ('', False), (None, False), (1, False), (1.2, False),
    (False, False), (True, False), (0, False),
    (['account.read', 'account.update', 'content.create', 'content.delete', 'content.read',
      'content.update', 'message.create', 'message.delete', 'message.read', 'message.update',
      'profile.read', 'profile.update'], True),
    (['account.read', 'account.update', 'content.create', 'content.delete', 'content.read',
      'content.update', 'message.create', 'message.delete', 'message.read', 'message.update',
      'profile.read', 'foo.read', 'profile.update'], False),
]
@pytest.mark.parametrize('perms, out', param)
# @pytest.mark.focus
def test_has_perms(tempdb, loop, perms, out):
    async def ab():
        await tempdb()
        user = await UserMod.get(email=VERIFIED_EMAIL_DEMO).only('id')
        assert await user.has_perm(*listify(perms)) == out
    loop.run_until_complete(ab())

# @pytest.mark.focus
# def test_user_data(loop):
#     async def ab():
#         return await user_data(VERIFIED_USER_DEMO)
#
#     user = loop.run_until_complete(ab())
#     ic(user)
#     # assert isinstance(user.id, UUID4)
#     # assert isinstance(user.groups, list)
#     # assert isinstance(user.is_active, bool)
#     # assert isinstance(user.options, dict)
#     # assert isinstance(user.email, str)
#     #
#     # with pytest.raises(AttributeError):
#     #     hasattr(user.permissions, 'permissions')




# param = [
#     ('settings.read', True),
#     (['settings.read'], True),
#     ('foo.read', False), (['foo.read'], False), (['foo.read', 'foo.update'], False),
#     (['settings.read', 'page.read'], True),
#     (('settings.read', 'page.read'), True),
#     (['settings.read', 'page.read', 'foo.read'], False),
#     ('', False), ([], False)
# ]
# @pytest.mark.parametrize('perms, out', param)
# # @pytest.mark.focus
# # @pytest.mark.skip
# def test_has_perm(client, headers, perms, out):
#     data = json.dumps(perms)
#     res = client.post('/test/dev_user_has_perms', headers=headers, data=data)
#     data = res.json()
#     assert data == out
#
#
# param = [
#     ('Temp1', True), (['Temp1'], True), (['Temp1', 'Temp2'], True),
#     ('', False), ([], False), (None, False), (True, False), (False, False),
# ]
# @pytest.mark.parametrize('data, out', param)
# # @pytest.mark.focus
# @pytest.mark.skip
# def test_remove_user_permissions(client, headers, data, out):
#     data = json.dumps(data)
#     res = client.post('/test/dev_remove_user_permissions', headers=headers, data=data)
#     data = res.json()
#     # assert data == out













# # @pytest.mark.focus
# @pytest.mark.skip
# def test_add_perm(client, headers):
#     res = client.post('/test/dev_user_add_perm', headers=headers)
#     data = res.json()
#     # ic(data)
#     assert data.get('id') == VERIFIED_USER_ID
#     assert data.get('email') == VERIFIED_EMAIL_DEMO
#     assert data.get('groups'), 'User needs to have at least one (1) group'
#     # assert data.get('permissions'), 'User needs to have at least one (1) permission'
#     # assert data.get('options'), 'User needs to have at least one (1) option'
