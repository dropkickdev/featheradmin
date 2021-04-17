import pytest, json
from tortoise.exceptions import DoesNotExist
from collections import Counter
from limeutils import listify

from app import red, ic
from app.settings import settings as s
from app.auth import Group, userdb
from tests.data import accountperms, noaddperms, contentperms, staffperms

param = [('FoobarGroup', 'Group summary for FoobarGroup'), ('MyGroup', 'Group summary for MyGroup')]
@pytest.mark.parametrize('name, summary', param)
# @pytest.mark.focus
def test_create_group(tempdb, loop, client, headers, name, summary):
    async def ab():
        await tempdb()
    loop.run_until_complete(ab())
    
    d = json.dumps(dict(name=name, summary=summary))
    res = client.post('/group', headers=headers, data=d)
    data = res.json()
    assert res.status_code == 200
    assert data
    
    async def cd():
        groups = await Group.all()
        for i in groups:
            if i.name == name:
                assert i.name == name
                assert i.summary == summary
    loop.run_until_complete(cd())


param = [
    (1, 'SomethingGroup', 'Take one', True), (1, '123', '', True),
    (3454, 'NotExistsGroup', 'Foobar', False),
]
@pytest.mark.parametrize('id, name, summary, out', param)
# @pytest.mark.focus
def test_update_group(tempdb, loop, client, headers, id, name, summary, out):
    try:
        async def ab():
            await tempdb()
            return await Group.get(pk=id).only('id', 'name', 'summary')
        oldgroup = loop.run_until_complete(ab())
        
        d = json.dumps(dict(id=id, name=name, summary=summary))
        res = client.patch('/group', headers=headers, data=d)
        success = res.json()
    
        async def cd():
            return await Group.get(pk=id).only('id', 'name', 'summary')
        newgroup = loop.run_until_complete(cd())
        
        assert success == out
        assert oldgroup.name != name
        assert newgroup.name == name
        assert newgroup.summary == summary
    except DoesNotExist:
        pass
    
    

# @pytest.mark.focus
# def test_foo(loop, tempdb):
#     async def ab():
#         x = await Option.all()
#         for i in x:
#             ic(i.name, i.value)
#
#     loop.run_until_complete(ab())


param = [
    ('AccountGroup', accountperms, True, 'QUERY'), ('AccountGroup', accountperms, False, 'CACHE'),
    ('NoaddGroup', noaddperms, True, 'QUERY'), ('NoaddGroup', noaddperms, False, 'CACHE'),
    ('ContentGroup', contentperms, True, 'QUERY'), ('ContentGroup', contentperms, False, 'CACHE'),
    ('AccountGroup', accountperms, False, 'CACHE'), ('NoaddGroup', noaddperms, False, 'CACHE'),
    ('ContentGroup', contentperms, False, 'CACHE'),
    (['AccountGroup', 'NoaddGroup'], accountperms + noaddperms, [False, False], ['CACHE', 'CACHE']),
    (['ContentGroup', 'AccountGroup'], contentperms + accountperms, [False, False], ['CACHE',
                                                                                     'CACHE']),
    (['ContentGroup', 'AccountGroup', 'StaffGroup'], contentperms + accountperms + staffperms,
     [False, False, True], ['CACHE', 'CACHE', 'QUERY']),
    (['ContentGroup', 'AccountGroup', 'StaffGroup'], contentperms + accountperms + staffperms,
     [False, False, False], ['CACHE', 'CACHE', 'CACHE']),
    (['ContentGroup', 'AccountGroup', 'StaffGroup'], contentperms + accountperms + staffperms,
     [True, False, False], ['QUERY', 'CACHE', 'CACHE']),
    (['ContentGroup', 'AccountGroup', 'StaffGroup'], contentperms + accountperms + staffperms,
     [False, True, False], ['CACHE', 'QUERY', 'CACHE']),
    (['ContentGroup', 'AccountGroup', 'StaffGroup'], contentperms + accountperms + staffperms,
     [False, False, False], ['CACHE', 'CACHE', 'CACHE']),
]
@pytest.mark.parametrize('groups, perms, remove, src', param)
@pytest.mark.focus
def test_get_permissions(loop, groups, perms, remove, src):
    async def ab():
        return await Group.get_permissions(userdb, *listify(groups), debug=True)

    groups = listify(groups)
    for idx, group in enumerate(groups):
        partialkey = s.CACHE_GROUPNAME.format(group)
        remove = listify(remove)
        if remove[idx]:
            red.delete(partialkey)
            assert not red.get(partialkey)
            assert not red.exists(partialkey)

    allperms, sources = loop.run_until_complete(ab())
    assert Counter(allperms) == Counter(perms)
    assert Counter(sources) == Counter(listify(src))
    

# param = [
#     ('user.create', ['AdminGroup', 'NoaddGroup']),
#     (['user.create'], ['AdminGroup', 'NoaddGroup']),
#     ('page.create', ['ContentGroup']),
#     (['user.create', 'page.create'], ['AdminGroup', 'NoaddGroup', 'ContentGroup']),
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

















# param = [
#     ('user.create', 'AdminGroup', True),
#     ('user.create', 'NoaddGroup', True),
#     ('page.create', 'ContentGroup', True),
#     ('page.create', 'NoaddGroup', False),
#     ('page.create', 'abc', False),
#     ('', 'abc', False),
#     ('page.create', '', False),
# ]
# @pytest.mark.parametrize('perm, group, out', param)
# @pytest.mark.focus
# def test_is_group(loop, perm, group, out):
#     async def ab():
#         assert await Permission.is_group(perm, group) == out
#     loop.run_until_complete(ab())


# # @pytest.mark.focus
# def test_abc(loop, tempdb):
#     from app.auth import Option
#
#     async def ab():
#         await tempdb()
#         await Option.create(name='foo', value='bar')
#         opt = await Option.all()
#         ic(opt)
#
#     loop.run_until_complete(ab())