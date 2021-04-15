from tortoise.manager import Manager
from tortoise.queryset import QuerySet


class Active(Manager):
    def get_queryset(self) -> QuerySet:
        return QuerySet(self._model).filter(is_active=True)