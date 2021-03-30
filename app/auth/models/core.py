from typing import Union
from tortoise import models, fields
from limeutils import modstr, listify

from app import red
# from app.auth.models.user import UserMod
# from app.auth.models.rbac import Group, Permission


class DTMixin(object):
    deleted_at = fields.DatetimeField(null=True)
    updated_at = fields.DatetimeField(auto_now=True)
    created_at = fields.DatetimeField(auto_now_add=True)


class UserGroupMixin(object):
    async def remove_perm(self, *perms):
        pass

    # TESTME: Untested
    async def add_perms(self, *perms) -> int:
        pass
        # """
        # Add permissions to either UserMod or Group
        # :param perms:   Permission codes
        # :return:        int Number of permissions added
        # """
        # perms = await Permission.filter(code__in=perms).only('id')
        # await self.permissions.add(*perms)    # noqa
        # return len(perms)


    # UPGRADE: Remove permissions from the current_user. It has no value.


    # TESTME: Untested
    async def remove_perms(self, remove: Union[str, list, tuple, set]) -> int:
        pass
        # # Get the list of perms
        # # Remove from that list if exists
        #
        # if isinstance(self, UserMod):
        #     perms = self.get_permissions(perm_type='user')
        #
        # elif isinstance(self, Group):
        #     # Get the perms for the group
        #     pass
        #
        # if not len(perms):
        #     return 0
        # remove = listify(remove)
        # diff = perms.difference_update(set(remove))
        # return len(perms) - len(diff)
    

class Option(models.Model):
    name = fields.CharField(max_length=20)
    value = fields.CharField(max_length=191)
    user = fields.ForeignKeyField('models.UserMod', related_name='options', null=True)
    is_active = fields.BooleanField(default=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = 'core_option'
        
    def __str__(self):
        return modstr(self, 'name')


class Taxonomy(DTMixin, models.Model):
    name = fields.CharField(max_length=191)
    type = fields.CharField(max_length=20)
    sort = fields.SmallIntField(default=100)
    author = fields.ForeignKeyField('models.UserMod', related_name='tax_of_author')
    parent = fields.ForeignKeyField('models.Taxonomy', related_name='tax_of_parent')
    
    class Meta:
        table = 'core_taxonomy'
    
    def __str__(self):
        return modstr(self, 'name')


class HashMod(models.Model):
    user = fields.ForeignKeyField('models.UserMod', related_name='hashes')
    hash = fields.CharField(max_length=199, index=True)
    use_type = fields.CharField(max_length=20)
    expires = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = 'auth_hash'
    
    def __str__(self):
        return modstr(self, 'hash')