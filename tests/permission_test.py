import pytest, json
from fastapi import status
from fastapi_users.utils import generate_jwt
from fastapi_users.router.verify import VERIFY_USER_TOKEN_AUDIENCE
from fastapi_users.utils import JWT_ALGORITHM

from app import ic, exceptions as x
from app.auth import Permission
from app.settings import settings as s



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

# param = [
#     ('user.create', ['NoAddGroup']),
#     (['user.create'], ['NoAddGroup']),
#     ('group.attach', ['StaffGroup', 'AdminGroup']),
#     (['group.attach', 'content.create'], ['StaffGroup', 'AdminGroup', 'ContentGroup']),
#     ([], [])
# ]
# @pytest.mark.parametrize('perm, out', param)
# # @pytest.mark.focus
# def test_permission_get_groups(loop, perm, out):
#     async def ab():
#         perms = listify(perm)
#         groups = await Permission.get_groups(*perms)
#         assert Counter(groups) == Counter(out)
#     loop.run_until_complete(ab())