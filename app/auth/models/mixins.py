from tortoise.query_utils import Prefetch

from app import ic, red, cache
from app.settings import settings as s


class UserMixin(object):
    async def get_and_cache(self, id: str, model=False):
        """
        Get a user's cachable data and cache it for future use. Replaces data if exists.
        Similar to the dependency current_user.
        :param id:      User id as str
        :param model:   Also return the UserMod instance
        :return:        DOESN'T NEED cache.restoreuser() since data is from the db not redis.
                        The id key in the hash is already formatted to a str from UUID.
        """
        query = self.model.get_or_none(pk=id) \
            .prefetch_related(
            Prefetch('groups', queryset=self.groupmodel.filter(deleted_at=None).only('id', 'name')),
            Prefetch('options', queryset=self.optionmodel.filter(is_active=True)
                     .only('user_id', 'name', 'value')),
            # Prefetch('permissions', queryset=Permission.filter(deleted_at=None).only('id', 'code'))
        )
        if self.oauth_account_model is not None:
            query = query.prefetch_related("oauth_accounts")
        usermod = await query.only(*self.select_fields)
        
        if usermod:
            user_dict = await usermod.to_dict(prefetch=True)
            partialkey = s.CACHE_USERNAME.format(id)
            red.set(partialkey, cache.prepareuser(user_dict), clear=True)
            
            if model:
                return self.usercomplete(**user_dict), usermod
            return self.usercomplete(**user_dict)