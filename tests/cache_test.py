import pytest
from ast import literal_eval

from app import ic, cache, red
from app.settings import settings as s
from app.auth.models import UserMod
from tests.auth_test import VERIFIED_EMAIL_DEMO


# @pytest.mark.focus
def test_prepareuser_dict(tempdb, loop):
    async def ab():
        await tempdb()
        usermod_temp = await UserMod.get(email=VERIFIED_EMAIL_DEMO).only('id')
        user, usermod = await usermod_temp.get_and_cache(usermod_temp.id, model=True)

        user_dict = await usermod.to_dict(prefetch=True)
        return cache.prepareuser_dict(user_dict)
    prepared = loop.run_until_complete(ab())

    assert len(prepared) == 10
    for k, v in prepared.items():
        if k in ['is_active', 'is_superuser', 'is_verified']:
            assert isinstance(v, int)
        else:
            assert isinstance(v, str)
            if k in ['groups', 'permissions']:
                data = literal_eval(v)
                assert isinstance(data, list)
            elif k in ['options']:
                data = dict(literal_eval(v))
                assert isinstance(data, dict)

# @pytest.mark.focus
def test_restoreuser_dict(tempdb, loop):
    async def ab():
        await tempdb()
        usermod_temp = await UserMod.get(email=VERIFIED_EMAIL_DEMO).only('id')
        await usermod_temp.get_and_cache(usermod_temp.id, model=True)

        partialkey = s.CACHE_USERNAME.format(usermod_temp.id)
        return red.get(partialkey)
    red_dict = loop.run_until_complete(ab())

    for k, v in red_dict.items():
        if k in ['is_active', 'is_superuser', 'is_verified']:
            assert isinstance(v, int)
        else:
            assert isinstance(v, str)

    restored = cache.restoreuser_dict(red_dict)
    for k, v in restored.items():
        if k in ['is_active', 'is_superuser', 'is_verified']:
            assert isinstance(v, bool)
        else:
            if k in ['groups', 'permissions']:
                assert isinstance(v, list)
            elif k in ['options']:
                assert isinstance(v, dict)
            else:
                assert isinstance(v, str)
        
    