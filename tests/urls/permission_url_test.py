import pytest, json

from app.auth import Permission

param = [
    (1, 'hello.world', 'Hello there', 204),
    (1, 'hello.there', 'Sup', 204),
    (1, 'hello', 'Sham', 204),
    (1, 'you.there', '', 204),
    (1, '', 'Shoo', 422),
    (1, '', '', 422),
]
@pytest.mark.parametrize('id, code, name, status', param)
# @pytest.mark.focus
def test_update_permission(loop, client, auth_headers_tempdb, id, code, name, status):
    headers, *_ = auth_headers_tempdb
    
    async def ab():
        return await Permission.get(pk=id).only('id', 'code', 'name')
    
    data = json.dumps(dict(id=id, code=code, name=name))
    res = client.patch('/permission', headers=headers, data=data)
    assert res.status_code == status
    
    if res.status_code == 204:
        perm = loop.run_until_complete(ab())
        assert perm.id == id
        assert perm.code == code
        assert perm.name == name


param = [
    ('foo.read', 204),
    ('user.create', 204)
]
@pytest.mark.parametrize('perm, status', param)
@pytest.mark.skip
def test_delete_permission(loop, client, auth_headers_tempdb, perm, status):
    pass
