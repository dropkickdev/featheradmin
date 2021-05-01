import pytest, json
from fastapi_users.utils import generate_jwt
from fastapi_users.router.verify import VERIFY_USER_TOKEN_AUDIENCE
from fastapi_users.utils import JWT_ALGORITHM

from app import ic
from app.auth import Permission
from app.settings import settings as s



param = [
    ('app.foo', 'App for Foo', 'App for Foo'), ('app.foo', '', 'App Foo'),
    ('app.foo.bar', '', 'App Foo Bar'), ('', 'Meh', ''),

]
@pytest.mark.parametrize('code, name, finalname', param)
# @pytest.mark.focus
def test_create_perm(loop, client, auth_headers_tempdb, code, name, finalname):
    headers, *_ = auth_headers_tempdb

    d = json.dumps(dict(code=code, name=name))
    res = client.post('/permission', headers=headers, data=d)
    assert res.status_code == 200
    data = res.json()
    
    if code:
        assert data.get('name') == finalname
        assert data.get('code') == code
    else:
        assert not data
