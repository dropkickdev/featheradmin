import pytest, json
from collections import Counter

from app import ic
from app.settings import settings as s


param = (
    ('StaffGroup', s.USER_GROUPS + ['StaffGroup']),
    ('AdminGroup', s.USER_GROUPS + ['AdminGroup']),
    ('xxx', s.USER_GROUPS), ('', s.USER_GROUPS)
)
@pytest.mark.parametrize('group, out', param)
# @pytest.mark.focus
def test_add_group_url(tempdb, loop, client, headers, group, out):
    async def ab():
        await tempdb()
    loop.run_until_complete(ab())
    
    data = json.dumps(group)
    res = client.post('/account/group', headers=headers, data=data)
    groups = res.json()
    if groups:
        assert Counter(groups) == Counter(out)
    else:
        assert groups is None