import pytest, json
from collections import Counter

from app.auth import Permission, UserMod
from app.tests.data import VERIFIED_EMAIL_DEMO
from app.fixtures.routes import enchance_only_perms as eperms



# @pytest.mark.focus
def test_update_permission(loop, client, auth_headers_tempdb):
    headers, *_ = auth_headers_tempdb
    
    async def ab():
        return await Permission.get(pk=id).only('id', 'code', 'name')
    
    param = [
        (1, 'hello.world', 'Hello there', 204),
        (1, 'hello.there', 'Sup', 204),
        (1, 'hello', 'Sham', 204),
        (1, 'you.there', '', 204),
        (1, '', 'Shoo', 422),
        (1, '', '', 422),
    ]
    for i in param:
        id, code, name, status = i
        
        data = json.dumps(dict(id=id, code=code, name=name))
        res = client.patch('/permission', headers=headers, data=data)
        assert res.status_code == status
        
        if res.status_code == 204:
            perm = loop.run_until_complete(ab())
            assert perm.id == id
            assert perm.code == code
            assert perm.name == name


# @pytest.mark.focus
def test_delete_permission(loop, client, auth_headers_tempdb):
    headers, *_ = auth_headers_tempdb
    
    param = [
        ('xxx', 200), ('ab', 422), ('foo.read', 204), ('user.create', 204)
    ]
    for i in param:
        perm, status = i
        
        data = json.dumps(perm)
        res = client.delete('/permission', headers=headers, data=data)
        assert res.status_code == status


# @pytest.mark.focus
def test_group_permission_attach(loop, client, auth_headers_tempdb):
    headers, *_ = auth_headers_tempdb
    
    param = [
        ('ContentGroup', 'user.create', 204),
        ('ContentGroup', ['user.create', 'user.delete'], 204),
        ('xxx', ['user.create', 'user.delete'], 200),
        ('ContentGroup', [''], 422), ('', [''], 422),
        ('ContentGroup', 'xxx', 200), ('RedGroup', 'xxx', 200),
        ('', [], 422), ('', '', 422), ('ContentGroup', '', 422), ('', 'user.create', 422)
    ]
    for i in param:
        group, code, status = i
        
        data = json.dumps(dict(name=group, codes=code))
        res = client.patch('/permission/attach/group', headers=headers, data=data)
        assert res.status_code == status


# @pytest.mark.focus
def test_group_permission_detach(loop, client, auth_headers_tempdb):
    headers, *_ = auth_headers_tempdb
    
    param = [
        ('ContentGroup', 'content.create', 204),
        ('ContentGroup', ['content.create', 'content.delete'], 204),
        ('xxx', ['user.create', 'user.delete'], 200),
        ('ContentGroup', [''], 422), ('', [''], 422),
        ('ContentGroup', 'xxx', 200), ('RedGroup', 'xxx', 200),
        ('', [], 422), ('', '', 422), ('ContentGroup', '', 422), ('', 'user.create', 422)
    ]
    for i in param:
        group, code, status = i
        
        data = json.dumps(dict(name=group, codes=code))
        res = client.delete('/permission/detach/group', headers=headers, data=data)
        assert res.status_code == status


param = [
    ('foo.read', eperms + ['foo.read'], 204),
    (['foo.read'], eperms + ['foo.read'], 204),
    ('foo.delete', eperms, 200), ('foo.hard_delete', eperms, 200),
    (['foo.read', 'foo.update'], eperms + ['foo.read', 'foo.update'], 204),
    (['foo.delete', 'foo.hard_delete'], eperms, 200),
    (['foo.read', 'xxx'], eperms + ['foo.read'], 204),
    (['xxx', 'foo.update'], eperms + ['foo.update'], 204),
    (['foo.read', ''], eperms + ['foo.read'], 204),
    (['', 'foo.update'], eperms + ['foo.update'], 204),
    ([''], eperms, 422), ([], eperms, 422), ('', eperms, 422),
    ('xxx', eperms, 200), (['xxx'], eperms, 200)
]
@pytest.mark.parametrize('codes, out, status', param)
# @pytest.mark.focus
def test_user_permission_attach(loop, client, auth_headers_tempdb, codes, out, status):
    headers, *_ = auth_headers_tempdb
    
    data = json.dumps(dict(codes=codes))
    res = client.patch('/permission/attach/user', headers=headers, data=data)
    assert res.status_code == status
    
    async def ab():
        usermod = await UserMod.get(email=VERIFIED_EMAIL_DEMO).only('id')
        return await usermod.get_permissions(perm_type='user')
    perms = loop.run_until_complete(ab())
    assert Counter(perms) == Counter(out)


param = [
    ('foo.delete', ['foo.hard_delete'], 204), ('foo.hard_delete', ['foo.delete'], 204),
    (['foo.delete'], ['foo.hard_delete'], 204), (['foo.hard_delete'], ['foo.delete'], 204),
    (['foo.delete', 'foo.hard_delete'], [], 204),
    (['foo.read', 'foo.update'], eperms, 200),
    (['foo.read', 'foo.delete'], ['foo.hard_delete'], 204),
    (['xxx', 'foo.delete'], ['foo.hard_delete'], 204),
    (['', 'foo.delete'], ['foo.hard_delete'], 204),
    ('foo.read', eperms, 200),
    (['xxx', 'xxx'], eperms, 200),
    ([''], eperms, 422), ([], eperms, 422), ('', eperms, 422),
    ('xxx', eperms, 200), (['xxx'], eperms, 200)
]
@pytest.mark.parametrize('codes, out, status', param)
# @pytest.mark.focus
def test_user_permission_detach(loop, client, auth_headers_tempdb, codes, out, status):
    headers, *_ = auth_headers_tempdb
    
    data = json.dumps(dict(codes=codes))
    res = client.delete('/permission/detach/user', headers=headers, data=data)
    assert res.status_code == status
    
    async def ab():
        usermod = await UserMod.get(email=VERIFIED_EMAIL_DEMO).only('id')
        return await usermod.get_permissions(perm_type='user')
    
    perms = loop.run_until_complete(ab())
    assert Counter(perms) == Counter(out)