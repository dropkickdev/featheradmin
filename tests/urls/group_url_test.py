import pytest, json
from collections import Counter

from app import ic
from app.settings import settings as s
from app.auth import Group



param = [
    ('ContentGroup', ['AccountGroup']), ('AccountGroup', ['ContentGroup']),
    ('xxx', s.USER_GROUPS), ('', s.USER_GROUPS)
]
@pytest.mark.parametrize('group, out', param)
# @pytest.mark.focus
def test_delete_group(tempdb, loop, client, auth_headers, group, out):
    headers, user = auth_headers
    
    data = json.dumps(group)
    res = client.delete('/group', headers=headers, data=data)
    assert res.status_code == 200, "You don't have permissions for this"

param = [
    ('SaladGroup', s.USER_GROUPS + ['SaladGroup']),
    ('AccountGroup', s.USER_GROUPS), ('', s.USER_GROUPS),
]
@pytest.mark.parametrize('group, out', param)
@pytest.mark.skip
def test_create_group(tempdb, loop, client, auth_headers, group, out):
    headers, user = auth_headers
    
    async def checker():
        return await Group.all().values_list('name', flat=True)
    
    data = json.dumps(dict(name=group, summary=''))
    res = client.post('/group', headers=headers, data=data)
    groups = res.json()
    
    allgroups = loop.run_until_complete(checker())
    assert res.status_code == 201, "You don't have permissions for this"
    assert Counter(allgroups) == Counter(groups)