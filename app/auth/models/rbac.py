from limeutils import modstr
from tortoise import models, fields

from app.auth.models.core import DTMixin


class HashMod(models.Model):
    user = fields.ForeignKeyField('models.UserMod', related_name='hashes')
    hash = fields.CharField(max_length=199)
    use_type = fields.CharField(max_length=20)
    expires = fields.DatetimeField(null=True)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = 'auth_hash'
    
    def __str__(self):
        return modstr(self, 'hash')
    

class UserPermissions(DTMixin, models.Model):
    user = fields.ForeignKeyField('models.UserMod', related_name='userpermissions')
    permission = fields.ForeignKeyField('models.Permission', related_name='userpermissions')
    
    class Meta:
        table = 'auth_user_permissions'
        unique_together = (('user_id', 'permission_id'),)


class UserGroups(DTMixin, models.Model):
    user = fields.ForeignKeyField('models.UserMod', related_name='usergroups')
    group = fields.ForeignKeyField('models.Group', related_name='usergroups')
    
    class Meta:
        table = 'auth_user_groups'
        unique_together = (('user_id', 'group_id'),)


class Group(models.Model):
    name = fields.CharField(max_length=191, index=True, unique=True)
    summary = fields.TextField(default='')
    deleted_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    
    # This table is automatically created with the name from 'through'. But if you want to
    # customize it then create a model and give it the same table name as the 'through'. Add any
    # fields you need in that custom model.
    permissions: models.ManyToManyRelation['Permission'] = \
        fields.ManyToManyField('models.Permission', related_name='groups',
                               through='auth_group_permissions')
    
    class Meta:
        table = 'auth_group'
    
    def __str__(self):
        return modstr(self, 'name')


class Permission(models.Model):
    name = fields.CharField(max_length=191, unique=True)
    code = fields.CharField(max_length=191, unique=True)
    deleted_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = 'auth_permission'
    
    def __str__(self):
        return modstr(self, 'name')


class GroupPermissions(models.Model):
    group = fields.ForeignKeyField('models.Group', related_name='grouppermissions')
    permission = fields.ForeignKeyField('models.Permission', related_name='grouppermissions')
    
    class Meta:
        table = 'auth_group_permissions'
        unique_together = (('group_id', 'permission_id'),)
    
    def __str__(self):
        return f'<{self.__class__.__name__}[{self.id}]>'  # noqa


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