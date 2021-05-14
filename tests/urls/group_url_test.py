import pytest, json
from collections import Counter

from app import logger
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
def test_delete_group(loop, client, auth_headers_tempdb, group, out, status):
    headers, *_ = auth_headers_tempdb
    
    data = json.dumps(group)
    res = client.delete('/group', headers=headers, data=data)
    assert res.status_code == status

param = [
    ('SaladGroup', s.USER_GROUPS + ['SaladGroup'], '', False, 201),
    ('SummaryGroup', s.USER_GROUPS + ['SaladGroup'], 'This is it', False, 201),
    ('AccountGroup', s.USER_GROUPS, '', False, 200), ('', s.USER_GROUPS, '', False, 200),
    ('SamsonGroup', s.USER_GROUPS + ['SamsonGroup'], 'Haha', False, 201),
]
@pytest.mark.parametrize('group, out, summary, debug, status', param)
@pytest.mark.focus
def test_create_group(loop, client, auth_headers_tempdb, group, out, summary, debug, status):
    headers, *_ = auth_headers_tempdb
    
    async def checker():
        groups = await Group.all().values('name', 'summary')
        return {i.get('name'):i.get('summary') for i in groups}

    data = json.dumps(dict(name=group, summary=summary))
    res = client.post('/group', headers=headers, data=data)
    data = res.json()
    
    allgroups = loop.run_until_complete(checker())
    assert res.status_code == status
    if res.status_code == 201:
        assert group in allgroups.keys()
        assert data.get('name') == group
        assert data.get('summary') == summary
        
