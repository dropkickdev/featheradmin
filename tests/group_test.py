import pytest, json
from tortoise.exceptions import DoesNotExist
from collections import Counter
from limeutils import listify

from app import red, ic
from app.settings import settings as s
from app.auth import Group
from tests.data import accountperms, noaddperms, contentperms, staffperms



param = [
    (1, 'SomethingGroup', 'Take one', 204),
    (2, '123', 'Masala', 204),
    (3454, 'NonExistsGroup', 'Foobar', 422),
    (1, '', '', 422), (1, [], '', 422), (1, None, '', 422),
]
@pytest.mark.parametrize('id, name, summary, status', param)
# @pytest.mark.focus
def test_update_group(loop, client, auth_headers_tempdb, id, name, summary, status):
    headers, *_ = auth_headers_tempdb

    data = json.dumps(dict(id=id, name=name, summary=summary))
    res = client.patch('/group', headers=headers, data=data)
    assert res.status_code == status

    async def ab():
        return await Group.get_or_none(pk=id).only('id', 'name', 'summary')

    group = loop.run_until_complete(ab())
    if res.status_code == 204:
        assert group.id == id
        assert group.name == name
        assert group.summary == summary

param = [
    ('AccountGroup', accountperms, True, 'QUERY'), ('AccountGroup', accountperms, False, 'CACHE'),
    ('NoaddGroup', noaddperms, True, 'QUERY'), ('NoaddGroup', noaddperms, False, 'CACHE'),
    ('ContentGroup', contentperms, True, 'QUERY'),
    ('ContentGroup', contentperms, False, 'CACHE'),
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
# @pytest.mark.focus
def test_get_permissions(tempdb, loop, groups, perms, remove, src):
    async def ab():
        await tempdb()
        return await Group.get_permissions(*listify(groups), debug=True)

    groups = listify(groups)
    for idx, group in enumerate(groups):
        partialkey = s.CACHE_GROUPNAME.format(group)
        remove = listify(remove)
        if remove[idx]:
            red.delete(partialkey)
            assert not red.get(partialkey)
            assert not red.exists(partialkey)

    loop.run_until_complete(ab())
    # ic(x)
    # allperms, sources = loop.run_until_complete(ab())
    # assert Counter(allperms) == Counter(perms)
    # assert Counter(sources) == Counter(listify(src))


















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
#     from app.authentication import Option
#
#     async def ab():
#         await tempdb()
#         await Option.create(name='foo', value='bar')
#         opt = await Option.all()
#         ic(opt)
#
#     loop.run_until_complete(ab())