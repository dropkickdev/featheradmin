import pytest, json
from collections import Counter

from app import ic
from tests.auth_test import VERIFIED_EMAIL_DEMO
from app.settings import settings as s
from app.auth import UserMod
from tests.data import accountperms, noaddperms, contentperms, staffperms
from fixtures.routes import enchance_only_perms



param = (
    ('StaffGroup', s.USER_GROUPS + ['StaffGroup']),
    ('AdminGroup', s.USER_GROUPS + ['AdminGroup']),
    ('xxx', s.USER_GROUPS), ('', s.USER_GROUPS)
)
@pytest.mark.parametrize('group, out', param)
# @pytest.mark.focus
def test_add_group_url(tempdb, loop, client, auth_headers_tempdb, group, out):
    headers, *_ = auth_headers_tempdb
    
    async def cd():
        usermod = await UserMod.get_or_none(email=VERIFIED_EMAIL_DEMO).only('id')
        return await usermod.get_groups(force_query=True)
    
    data = json.dumps(group)
    res = client.post('/account/group', headers=headers, data=data)
    groups = res.json()
    
    assert res.status_code == 201
    if groups:
        dbgroups = loop.run_until_complete(cd())
        assert Counter(groups) == Counter(out)
        assert Counter(dbgroups) == Counter(out)
    else:
        assert groups is None


param = (
    ('AccountGroup', ['ContentGroup']),
    ('ContentGroup', ['AccountGroup']),
    ('xxx', s.USER_GROUPS), ('', s.USER_GROUPS)
)
@pytest.mark.parametrize('group, out', param)
# @pytest.mark.focus
def test_remove_group_url(tempdb, loop, client, auth_headers_tempdb, group, out):
    headers, *_ = auth_headers_tempdb

    async def ab():
        usermod = await UserMod.get_or_none(email=VERIFIED_EMAIL_DEMO).only('id')
        return await usermod.get_groups(force_query=True)
    
    data = json.dumps(group)
    res = client.delete('/account/group', headers=headers, data=data)
    groups = res.json()
    
    assert res.status_code == 200
    if groups:
        dbgroups = loop.run_until_complete(ab())
        assert Counter(groups) == Counter(out)
        assert Counter(dbgroups) == Counter(out)
    else:
        assert groups is None



param = (
    ('', enchance_only_perms),
    ('foo.read', list(set(enchance_only_perms + ['foo.read']))),
    (['foo.read', 'foo.delete'], list(set(enchance_only_perms + ['foo.read', 'foo.delete']))),
    (enchance_only_perms, enchance_only_perms),
    (['xxx', 'foo.read'], list(set(enchance_only_perms + ['foo.read']))),
    (['', 'foo.read'], list(set(enchance_only_perms + ['foo.read']))),
    (['', ''], enchance_only_perms)
)
@pytest.mark.parametrize('perms, out', param)
# @pytest.mark.focus
def test_add_permission_url(tempdb, loop, client, headers, perms, out):
    async def ab():
        await tempdb()
    loop.run_until_complete(ab())
    
    async def cd():
        usermod = await UserMod.get_or_none(email=VERIFIED_EMAIL_DEMO).only('id')
        return await usermod.get_permissions(perm_type='user')

    data = json.dumps(perms)
    res = client.post('/account/permission', headers=headers, data=data)
    perms = res.json()

    assert res.status_code == 201
    dbperms = loop.run_until_complete(cd())
    assert Counter(perms) == Counter(out)
    assert Counter(dbperms) == Counter(out)


param = (
    ('foo.delete', ['foo.hard_delete']), (['foo.hard_delete'], ['foo.delete']),
    (['foo.delete', 'foo.hard_delete'], []),
    ('xxx', enchance_only_perms), ('', enchance_only_perms),
    (['', ''], enchance_only_perms)
)
@pytest.mark.parametrize('perms, out', param)
# @pytest.mark.focus
def test_add_permission_url(tempdb, loop, client, auth_headers_tempdb, perms, out):
    headers, *_ = auth_headers_tempdb
    
    async def checker():
        usermod = await UserMod.get_or_none(email=VERIFIED_EMAIL_DEMO).only('id')
        return await usermod.get_permissions(perm_type='user')
    
    data = json.dumps(perms)
    res = client.delete('/account/permission', headers=headers, data=data)
    perms = res.json()
    
    assert res.status_code == 200
    dbperms = loop.run_until_complete(checker())
    assert Counter(perms) == Counter(out)
    assert Counter(dbperms) == Counter(out)

param = [
    ('profile.read', True), (['profile.read'], True),
    ('foo.read', False), (['foo.read'], False),
    (['foo.read', 'foo.update'], False),
    (['profile.read', 'content.read'], True),
    (('profile.read', 'content.read'), True),
    (['profile.read', 'content.read', 'foo.read'], False),
    (['foo.read', 'foo.update', 'foo.create'], False),
    (['profile.read', 'content.read', 'foo.delete'], True),
    ('', False), ([], False)
]
@pytest.mark.parametrize('perms, out', param)
# @pytest.mark.focus
def test_has_perm_url(client, auth_headers_tempdb, perms, out):
    headers, *_ = auth_headers_tempdb
    
    data = json.dumps(perms)
    res = client.post('/account/has-perm', headers=headers, data=data)
    data = res.json()
    assert data == out