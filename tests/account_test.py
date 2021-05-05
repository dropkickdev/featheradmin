import pytest, json
from collections import Counter
from uuid import UUID
from limeutils import listify

from app import ic, cache
from app.auth import userdb
from app.cache import red
from app.settings import settings as s
from .auth_test import VERIFIED_ID_DEMO, VERIFIED_EMAIL_DEMO
from app.auth.models import UserMod, UserDBComplete, Group, Permission, UserPermissions
from .data import accountperms, noaddperms, contentperms, staffperms



@pytest.mark.userdata
def test_current_user_data(loop, client, passwd, auth_headers_tempdb):
    headers, *_ = auth_headers_tempdb
    res = client.post('/test/dev_user_data', headers=headers)
    data = res.json()

    user = UserDBComplete(**data)
    assert isinstance(user.id, str)
    assert isinstance(user.email, str)
    assert isinstance(user.is_active, bool)
    assert isinstance(user.is_verified, bool)
    assert isinstance(user.is_superuser, bool)
    assert isinstance(user.username, str)
    assert isinstance(user.timezone, str)
    assert isinstance(user.groups, list)
    assert isinstance(user.permissions, list)
    assert isinstance(user.options, dict)

# @pytest.mark.focus
def test_get_and_cache(tempdb, loop):
    async def ab():
        await tempdb()
        usermod = await UserMod.get(email=VERIFIED_EMAIL_DEMO).only('id')
        partialkey = s.CACHE_USERNAME.format(usermod.id)

        red.delete(partialkey)
        query_data = await usermod.get_and_cache(usermod.id)
        assert red.exists(partialkey)
        cache_data = UserDBComplete(**cache.restoreuser_dict(red.get(partialkey)))
        return query_data, cache_data
    query_data, cache_data = loop.run_until_complete(ab())

    assert isinstance(query_data.id, str)
    assert isinstance(query_data.email, str)
    assert isinstance(query_data.is_active, bool)
    assert isinstance(query_data.is_verified, bool)
    assert isinstance(query_data.is_superuser, bool)
    assert isinstance(query_data.username, str)
    assert isinstance(query_data.timezone, str)
    assert isinstance(query_data.groups, list)
    assert isinstance(query_data.options, dict)

    assert isinstance(cache_data.id, str)
    assert isinstance(cache_data.email, str)
    assert isinstance(cache_data.is_active, bool)
    assert isinstance(cache_data.is_verified, bool)
    assert isinstance(cache_data.is_superuser, bool)
    assert isinstance(cache_data.username, str)
    assert isinstance(cache_data.timezone, str)
    assert isinstance(cache_data.groups, list)
    assert isinstance(cache_data.options, dict)

    assert query_data.id == cache_data.id
    assert query_data.email == cache_data.email
    assert query_data.is_active == cache_data.is_active
    assert query_data.is_verified == cache_data.is_verified
    assert query_data.is_superuser == cache_data.is_superuser
    assert query_data.username == cache_data.username
    assert query_data.timezone == cache_data.timezone
    assert Counter(query_data.groups) == Counter(cache_data.groups)

    assert len(query_data.options) == len(cache_data.options)
    for k, v in query_data.options.items():
        assert cache_data.options[k] == v

# @pytest.mark.focus
def test_get_data(tempdb, loop):
    async def ab():
        await tempdb()
        usermod = await UserMod.get(email=VERIFIED_EMAIL_DEMO).only('id')
        partialkey = s.CACHE_USERNAME.format(usermod.id)

        user, source = await usermod.get_data(debug=True)
        assert source == 'QUERY'
        user, source = await usermod.get_data(debug=True)
        assert source == 'CACHE'
        user, source = await usermod.get_data(debug=True)
        assert source == 'CACHE'

        red.delete(partialkey)
        user, source = await usermod.get_data(debug=True)
        assert source == 'QUERY'
        user, source = await usermod.get_data(debug=True)
        assert source == 'CACHE'
        user, source = await usermod.get_data(debug=True)
        assert source == 'CACHE'

        user, source = await usermod.get_data(debug=True, force_query=True)
        assert source == 'QUERY'
        user, source = await usermod.get_data(debug=True, force_query=True)
        assert source == 'QUERY'
        user, source = await usermod.get_data(debug=True)
        assert source == 'CACHE'
    loop.run_until_complete(ab())

# @pytest.mark.focus
def test_get_groups(tempdb, loop):
    async def ab():
        await tempdb()
        usermod = await UserMod.get(email=VERIFIED_EMAIL_DEMO).only('id')
        partialkey = s.CACHE_USERNAME.format(usermod.id)

        red.delete(partialkey)
        groups, source = await usermod.get_groups(debug=True)
        assert Counter(groups) == Counter(s.USER_GROUPS)
        assert source == 'QUERY'

        groups, source = await usermod.get_groups(debug=True)
        assert Counter(groups) == Counter(s.USER_GROUPS)
        assert source == 'CACHE'

        groups, source = await usermod.get_groups(debug=True)
        assert Counter(groups) == Counter(s.USER_GROUPS)
        assert source == 'CACHE'

        red.delete(partialkey)
        groups, source = await usermod.get_groups(debug=True)
        assert Counter(groups) == Counter(s.USER_GROUPS)
        assert source == 'QUERY'

        groups, source = await usermod.get_groups(debug=True)
        assert Counter(groups) == Counter(s.USER_GROUPS)
        assert source == 'CACHE'

        data = await usermod.get_groups()
        assert isinstance(data, list)
        assert Counter(data) == Counter(s.USER_GROUPS)
    loop.run_until_complete(ab())

# @pytest.mark.focus
def test_has_group(tempdb, loop):
    async def ab():
        await tempdb()
        user = await UserMod.get_or_none(email=VERIFIED_EMAIL_DEMO).only('id')
        
        assert await user.has_group(s.USER_GROUPS[0])
        assert await user.has_group(s.USER_GROUPS[1])
        assert await user.has_group(s.USER_GROUPS[0], s.USER_GROUPS[1])
        assert not await user.has_group('NoaddGroup')
        assert not await user.has_group(s.USER_GROUPS[0], 'NoaddGroup')
        assert not await user.has_group(s.USER_GROUPS[0], s.USER_GROUPS[1], 'NoaddGroup')
    loop.run_until_complete(ab())
    
# @pytest.mark.focus
def test_add_group(tempdb, loop):
    mergedgroups = s.USER_GROUPS + ['StaffGroup', 'NoaddGroup']
    param = (
        ('StaffGroup', s.USER_GROUPS + ['StaffGroup']),
        (['StaffGroup'], s.USER_GROUPS + ['StaffGroup']),
        (['StaffGroup', 'NoaddGroup'], mergedgroups),
        (['StaffGroup', 'xxx'], mergedgroups),
        (['StaffGroup', None], mergedgroups),
        (['StaffGroup', ''], mergedgroups),
        (['StaffGroup', False], mergedgroups),
        (['StaffGroup', True], mergedgroups),
        ('', mergedgroups),
        (None, mergedgroups),
        (s.USER_GROUPS, mergedgroups),
        (['', None, False, True], mergedgroups),
        (['', None, False, True, 'StaffGroup'], mergedgroups),
        ([True, True, True], mergedgroups), ([None, None, None], mergedgroups),
        ('AdminGroup', mergedgroups + ['AdminGroup']),
    )
    async def ab():
        await tempdb()
        usermod = await UserMod.get(email=VERIFIED_EMAIL_DEMO).only('id')
        partialkey = s.CACHE_USERNAME.format(usermod.id)
        await usermod.get_and_cache(usermod.id)

        groups = await usermod.get_groups()
        assert Counter(groups) == Counter(s.USER_GROUPS)
        cached_groups = UserDBComplete(**cache.restoreuser_dict(red.get(partialkey))).groups
        assert Counter(groups) == Counter(cached_groups)

        for i in param:
            addgroups, out = i

            newgroups = await usermod.add_group(*listify(addgroups))
            if newgroups:
                assert Counter(newgroups) == Counter(out)

            updatedgroups = await usermod.get_groups()
            if updatedgroups:
                assert Counter(updatedgroups) == Counter(out)

            cached_groups = userdb.usercomplete(**cache.restoreuser_dict(red.get(partialkey))).groups
            if cached_groups:
                assert Counter(cached_groups) == Counter(out)
    loop.run_until_complete(ab())

# @pytest.mark.focus
def test_remove_group(tempdb, loop):
    param = (
        ('', ['StaffGroup', 'AdminGroup', 'NoaddGroup', 'ContentGroup', 'AccountGroup']),
        ('AccountGroup', ['StaffGroup', 'AdminGroup', 'NoaddGroup', 'ContentGroup']),
        (['ContentGroup'], ['StaffGroup', 'AdminGroup', 'NoaddGroup']),
        (['AdminGroup', 'NoaddGroup'], ['StaffGroup']),
    )

    async def ab():
        await tempdb()
        usermod = await UserMod.get(email=VERIFIED_EMAIL_DEMO).only('id')
        if usermod:
            groups = await usermod.add_group('StaffGroup', 'AdminGroup', 'NoaddGroup')
            assert Counter(groups) == Counter(['StaffGroup', 'AdminGroup', 'NoaddGroup',
                                               'ContentGroup', 'AccountGroup'])
        for i in param:
            removegroup, out = i
            afterremove = await usermod.remove_group(*listify(removegroup))
            assert Counter(afterremove) == Counter(out)

            partialkey = s.CACHE_USERNAME.format(usermod.id)
            cached_groups = userdb.usercomplete(**cache.restoreuser_dict(red.get(partialkey))).groups
            assert Counter(cached_groups) == Counter(out)
    loop.run_until_complete(ab())

# @pytest.mark.focus
def test_update_groups(tempdb, loop):
    param = (
        (['AccountGroup', 'AdminGroup'], ['AccountGroup', 'AdminGroup']),
        (['AccountGroup', 'ContentGroup'], ['AccountGroup', 'ContentGroup']),
        (['StaffGroup'], ['StaffGroup']), (['StaffGroup', 'NoaddGroup'], ['StaffGroup', 'NoaddGroup']),
        ([None, None], ['StaffGroup', 'NoaddGroup']), (['', ''], ['StaffGroup', 'NoaddGroup']),
        (['xxx', 'yyy'], ['StaffGroup', 'NoaddGroup']),
        (['xxx', 'StaffGroup'], ['StaffGroup'])
    )
    async def ab():
        await tempdb()
        for i in param:
            groups, out = i
            user = await UserMod.get(email=VERIFIED_EMAIL_DEMO).only('id')
            partialkey = s.CACHE_USERNAME.format(user.id)

            queried = await user.get_groups(force_query=True)
            cached = UserDBComplete(**cache.restoreuser_dict(red.get(partialkey))).groups
            assert Counter(queried) == Counter(cached)

            updated = await user.update_groups(groups)
            if updated:
                assert Counter(updated) == Counter(out)
    loop.run_until_complete(ab())

# @pytest.mark.focus
def test_get_permissions(tempdb, loop):
    starterperms = list(set(accountperms + contentperms + ['foo.delete', 'foo.hard_delete']))
    param = (
        ('', starterperms), ('xxx', starterperms), (None, starterperms), ([], starterperms),
        (None, starterperms), ('StaffGroup', list(set(starterperms + staffperms))),
        (['StaffGroup', 'xxx'], list(set(starterperms + staffperms))),
        (['StaffGroup', 'NoaddGroup'], list(set(starterperms + staffperms + noaddperms))),
    )
    async def ab():
        await tempdb()
        usermod = await UserMod.get(email=VERIFIED_EMAIL_DEMO).only('id')

        perms = await usermod.get_permissions()
        assert Counter(perms) == Counter(starterperms)

        for i in param:
            addgroups, out = i
            await usermod.add_group(*listify(addgroups))
            perms = await usermod.get_permissions()
            if perms:
                assert Counter(perms) == Counter(out)
    loop.run_until_complete(ab())

# @pytest.mark.focus
def test_has_perm(tempdb, loop):
    param = (
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
    )
    
    async def ab():
        await tempdb()
        usermod = await UserMod.get(email=VERIFIED_EMAIL_DEMO).only('id')
        for i in param:
            perms, out = i
            assert await usermod.has_perm(*listify(perms)) == out
    loop.run_until_complete(ab())






















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
