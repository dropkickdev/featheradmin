import pytest, json

from app import ic
from app.settings import settings as s



param = [
    ('ContentGroup', ['AccountGroup']), ('AccountGroup', ['ContentGroup']),
    ('xxx', s.USER_GROUPS), ('', s.USER_GROUPS)
]
@pytest.mark.parametrize('group, out', param)
# @pytest.mark.focus
def test_delete_group(tempdb, loop, client, headers, group, out):
    async def ab():
        await tempdb()
    loop.run_until_complete(ab())
    
    data = json.dumps(group)
    res = client.delete('/group', headers=headers, data=data)
    assert res.status_code == 200, "You don't have permissions for this"