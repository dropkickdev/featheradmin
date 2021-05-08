import pytest, json
from collections import Counter

from app import ic, exceptions as x
from app.settings import settings as s
from app.auth import Group



param = [
    ('ContentGroup', ['AccountGroup'], 204),
    ('AccountGroup', ['ContentGroup'], 204),
    ('xxx', s.USER_GROUPS, x.UNPROCESSABLE_422),
    ('', s.USER_GROUPS, x.UNPROCESSABLE_422)
]
@pytest.mark.parametrize('group, out, status', param)
# @pytest.mark.focus
def test_delete_group(tempdb, loop, client, auth_headers_tempdb, group, out, status):
    headers, *_ = auth_headers_tempdb
    
    data = json.dumps(group)
    res = client.delete('/group', headers=headers, data=data)
    assert res.status_code == status

param = [
    ('SaladGroup', s.USER_GROUPS + ['SaladGroup']),
    ('AccountGroup', s.USER_GROUPS), ('', s.USER_GROUPS),
]
@pytest.mark.parametrize('group, out', param)
@pytest.mark.skip
def test_create_group(tempdb, loop, client, auth_headers_tempdb, group, out):
    headers, *_ = auth_headers_tempdb
    
    async def checker():
        return await Group.all().values_list('name', flat=True)
    
    data = json.dumps(dict(name=group, summary=''))
    res = client.post('/group', headers=headers, data=data)
    groups = res.json()
    
    allgroups = loop.run_until_complete(checker())
    assert res.status_code == 201
    assert Counter(allgroups) == Counter(groups)