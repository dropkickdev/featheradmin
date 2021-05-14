import pytest, json
from collections import Counter
from fastapi import status
from fastapi_users.utils import generate_jwt
from fastapi_users.router.verify import VERIFY_USER_TOKEN_AUDIENCE
from fastapi_users.utils import JWT_ALGORITHM
from limeutils import listify

from app import ic, exceptions as x
from app.auth import Permission
from app.settings import settings as s
from app.pydantic import UpdatePermissionPy



param = [
    ('app.foo', 'App for Foo', 'App for Foo', 201), ('app.foo', '', 'App Foo', 201),
    ('app.foo.bar', '', 'App Foo Bar', 201), ('', 'Meh', '', x.UNPROCESSABLE_422),
]
@pytest.mark.parametrize('code, name, finalname, status', param)
# @pytest.mark.focus
def test_create_perm(loop, client, auth_headers_tempdb, code, name, finalname, status):
    headers, *_ = auth_headers_tempdb

    d = json.dumps(dict(code=code, name=name))
    res = client.post('/permission', headers=headers, data=d)
    data = res.json()
    
    if code:
        assert data.get('name') == finalname
        assert data.get('code') == code
    assert res.status_code == status

param = [
    ('foo.read', ['NoaddGroup']),
    (['foo.read'], ['NoaddGroup']),
    ('user.read', ['StaffGroup', 'AdminGroup']),
    (['foo.read', 'foo.update'], ['NoaddGroup']),
    (['foo.read', 'foo.update', 'user.create'], ['StaffGroup', 'AdminGroup', 'NoaddGroup']),
    ([], []), ('', [])
]
@pytest.mark.parametrize('perms, out', param)
# @pytest.mark.focus
def test_permission_get_groups(tempdb, loop, perms, out):
    async def ab():
        await tempdb()
        groups = await Permission.get_groups(*listify(perms))
        assert Counter(groups) == Counter(out)
    loop.run_until_complete(ab())

# TODO: Add more tests
param = [
    (1, 'hello.world', 'Hello there', 204)
]
@pytest.mark.parametrize('id, code, name, status', param)
@pytest.mark.focus
def test_update_permission(loop, client, auth_headers_tempdb, id, code, name, status):
    headers, *_ = auth_headers_tempdb
    
    async def ab():
        return await Permission.get(pk=id).only('id', 'code', 'name')
    
    data = json.dumps(dict(id=id, code=code, name=name))
    res = client.patch('/permission', headers=headers, data=data)
    assert res.status_code == status

    perm = loop.run_until_complete(ab())
    assert perm.id == id
    assert perm.code == code
    assert perm.name == name
