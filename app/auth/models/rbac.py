from limeutils import modstr
from tortoise import models, fields

from app import ic, red
from app.settings import settings as s
from app.auth.models.core import DTMixin


class UserPermissions(models.Model):
    user = fields.ForeignKeyField('models.UserMod', related_name='userpermissions')
    permission = fields.ForeignKeyField('models.Permission', related_name='userpermissions')
    author = fields.ForeignKeyField('models.UserMod', related_name='userpermissions_author')
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = 'auth_user_permissions'
        unique_together = (('user_id', 'permission_id'),)


# class UserGroups(models.Model):
#     user = fields.ForeignKeyField('models.UserMod', related_name='usergroups')
#     group = fields.ForeignKeyField('models.Group', related_name='usergroups')
#
#     class Meta:
#         table = 'auth_user_groups'
#         unique_together = (('user_id', 'group_id'),)


class Group(models.Model):
    name = fields.CharField(max_length=191, index=True, unique=True)
    summary = fields.TextField(default='')
    deleted_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    
    permissions: models.ManyToManyRelation['Permission'] = \
        fields.ManyToManyField('models.Permission', related_name='groups',
                               through='auth_group_permissions', backward_key='group_id')
    
    class Meta:
        table = 'auth_group'
    
    def __str__(self):
        return modstr(self, 'name')
    
    @classmethod
    async def get_permissions(cls, name) -> list:
        """
        Get permissions of a group. Uses cache else query.
        :param name:    Name of a group
        :return:        list List of permissions for that group
        """
        if red.exists(name):
            return red.get(s.CACHE_GROUPNAME.format(name))
        else:
            perms = await Permission.filter(groups__name=name).values('code')
            allperms = [i.get('code') for i in perms]
            red.set(s.CACHE_GROUPNAME.format(name), allperms)
            return allperms


class Permission(models.Model):
    name = fields.CharField(max_length=191, unique=True)
    code = fields.CharField(max_length=191, index=True, unique=True)
    deleted_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = 'auth_permission'
    
    def __str__(self):
        return modstr(self, 'name')


# class GroupPermissions(models.Model):
#     auth_group = fields.ForeignKeyField('models.Group', related_name='grouppermissions')
#     permission = fields.ForeignKeyField('models.Permission', related_name='grouppermissions')
#
#     class Meta:
#         table = 'auth_group_permissions'
#         unique_together = (('auth_group_id', 'permission_id'),)
#
#     def __str__(self):
#         return f'<{self.__class__.__name__}[{self.id}]>'  # noqa


class Taxonomy(DTMixin, models.Model):
    name = fields.CharField(max_length=191)
    type = fields.CharField(max_length=20)
    sort = fields.SmallIntField(default=100)
    author = fields.ForeignKeyField('models.UserMod', related_name='author_taxs')
    parent = fields.ForeignKeyField('models.Taxonomy', related_name='parent_taxs')
    
    class Meta:
        table = 'core_taxonomy'
    
    def __str__(self):
        return modstr(self, 'name')