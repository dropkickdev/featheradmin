from tortoise import models, fields
from limeutils import model_str


class DTMixin(object):
    deleted_at = fields.DatetimeField(null=True)
    updated_at = fields.DatetimeField(auto_now=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    

class Option(models.Model):
    name = fields.CharField(max_length=20)
    value = fields.CharField(max_length=191)
    user = fields.ForeignKeyField('models.User', related_name='options', null=True)
    is_active = fields.BooleanField(default=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    
    class Meta:
        table = 'core_option'


class Taxonomy(DTMixin, models.Model):
    name = fields.CharField(max_length=191)
    type = fields.CharField(max_length=20)
    sort = fields.SmallIntField(default=100)
    author = fields.ForeignKeyField('models.User', related_name='tax_of_author')
    parent = fields.ForeignKeyField('models.Taxonomy', related_name='tax_of_parent')
    
    class Meta:
        table = 'core_taxonomy'
    
    def __str__(self):
        return model_str(self, 'name')


class Token(models.Model):
    token = fields.CharField(max_length=128, index=True)
    expires = fields.DatetimeField(index=True)
    is_blacklisted = fields.BooleanField(default=False)
    author = fields.ForeignKeyField('models.User', on_delete=fields.CASCADE,
                                    related_name='author_tokens')
    
    class Meta:
        table = 'auth_token'
    
    def __str__(self):
        return model_str(self, 'token')
