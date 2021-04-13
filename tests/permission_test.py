import pytest, json

from app import ic
from app.auth import Permission

param = [
    ('app.foo', 'App for Foo', 'App for Foo'), ('app.foo', '', 'App Foo'),
    ('app.foo.bar', '', 'App Foo Bar'), ('', 'Meh', ''),
    
]
@pytest.mark.parametrize('code, name, finalname', param)
# @pytest.mark.focus
def test_create_perm(tempdb, loop, client, headers, code, name, finalname):
    async def ab():
        await tempdb()
    loop.run_until_complete(ab())
    
    d = json.dumps(dict(code=code, name=name))
    
    res = client.post('/permission', headers=headers, data=d)
    assert res.status_code == 200
    data = res.json()
    if code:
        assert data.get('name') == finalname
        assert data.get('code') == code
    else:
        assert not data
