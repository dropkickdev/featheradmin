from tortoise.manager import Manager
from tortoise.queryset import QuerySet


class Active(Manager):
    def get_queryset(self) -> QuerySet:
        qs = super().get_queryset()
        if hasattr(self._model, "deleted_at"):
            qs = qs.filter(deleted_at=None)
        if hasattr(self._model, "is_active"):
            qs = qs.filter(is_active=True)
        return qs
        # return QuerySet(self._model).filter(is_active=True)