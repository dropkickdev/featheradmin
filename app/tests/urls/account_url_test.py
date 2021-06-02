import pytest, json
from collections import Counter

from app.tests.auth_test import VERIFIED_EMAIL_DEMO
from app.settings import settings as s
from app.auth import UserMod
from fixtures.routes import enchance_only_perms



param = (
    ('StaffGroup', 204),
    ('AdminGroup', 204),
    ('xxx', 200),
    ('', 422)
)
@pytest.mark.parametrize('group, status', param)
# @pytest.mark.focus
def test_attach_group_url(client, auth_headers_tempdb, group, status):
    headers, *_ = auth_headers_tempdb
    
    data = json.dumps(group)
    res = client.patch('/account/group/attach', headers=headers, data=data)
    assert res.status_code == status

param = (
    ('AccountGroup', ['ContentGroup'], 204),
    ('ContentGroup', ['AccountGroup'], 204),
    ('xxx', s.USER_GROUPS, 204),
    ('', s.USER_GROUPS, 422),
)
@pytest.mark.parametrize('group, out, status', param)
# @pytest.mark.focus
def test_detach_group_url(loop, client, auth_headers_tempdb, group, out, status):
    headers, *_ = auth_headers_tempdb

    async def ab():
        usermod = await UserMod.get_or_none(email=VERIFIED_EMAIL_DEMO).only('id')
        return await usermod.get_groups(force_query=True)
    
    data = json.dumps(group)
    res = client.patch('/account/group/detach', headers=headers, data=data)
    
    assert res.status_code == status
    dbgroups = loop.run_until_complete(ab())
    assert Counter(dbgroups) == Counter(out)

param = (
    ('', 422),
    ('foo.read', 204),
    (['foo.read', 'foo.delete'], 204),
    (enchance_only_perms, 200),
    (['xxx', 'foo.read'], 204),
    (['', 'foo.read'], 204),
    (['', ''], 200)
)
@pytest.mark.parametrize('perms, status', param)
# @pytest.mark.focus
def test_attach_permission_url(client, auth_headers_tempdb, perms, status):
    headers, *_ = auth_headers_tempdb
    
    data = json.dumps(perms)
    res = client.patch('/account/permission/attach', headers=headers, data=data)
    assert res.status_code == status

param = (
    ('foo.delete', ['foo.hard_delete']), (['foo.hard_delete'], ['foo.delete']),
    (['foo.delete', 'foo.hard_delete'], []),
    ('xxx', enchance_only_perms), ('', enchance_only_perms),
    (['', ''], enchance_only_perms)
)
@pytest.mark.parametrize('perms, out', param)
# @pytest.mark.focus
def test_detach_permission_url(loop, client, auth_headers_tempdb, perms, out):
    headers, user, _ = auth_headers_tempdb
    
    async def ab():
        usermod = await UserMod.get_or_none(email=VERIFIED_EMAIL_DEMO).only('id')
        return await usermod.get_permissions(perm_type='user')
    
    data = json.dumps(perms)
    client.patch('/account/permission/detach', headers=headers, data=data)
    
    dbperms = loop.run_until_complete(ab())
    # ic(dbperms)
    assert Counter(dbperms) == Counter(out)

param = [
    ('profile.read', True),
    (['profile.read'], True),
    ('foo.read', False),
    (['foo.read'], False), (['xxx'], False),
    (['profile.read', 'xxx'], False), (['profile.read', 'xxx', 'content.read'], False),
    (['foo.read', 'foo.update'], False),
    (['profile.read', 'content.read'], True),
    (('profile.read', 'content.read'), True),
    (['profile.read', 'content.read', 'foo.read'], False),
    (['foo.read', 'foo.update', 'foo.create'], False),
    (['profile.read', 'content.read', 'foo.delete'], True),
    ('foo.delete', True), ('foo.read', False),
    ('', False), ([], False),
]
@pytest.mark.parametrize('perms, out', param)
# @pytest.mark.focus
def test_has_perm_url(client, auth_headers_tempdb, perms, out):
    headers, *_ = auth_headers_tempdb
    
    data = json.dumps(dict(perms=perms, superuser=False))
    res = client.post('/account/has-perm', headers=headers, data=data)
    data = res.json()
    assert data == out