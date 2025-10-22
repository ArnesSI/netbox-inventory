from django.db import models

from utilities.querysets import RestrictedQuerySet


class AssetManager(models.Manager.from_queryset(RestrictedQuerySet)):
    def count_with_children(self):
        """ """
        if hasattr(self, 'instance'):
            assets = self.model.objects.filter(
                storage_location__in=self.instance.get_descendants(include_self=True)
            )
        else:
            assets = self.get_queryset()
        return assets.count()
