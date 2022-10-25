from django.dispatch import receiver
from django.db.models.signals import post_save

from dcim.models import Device, Module, InventoryItem
from .models import Asset


@receiver(post_save, sender=Device)
@receiver(post_save, sender=Module)
@receiver(post_save, sender=InventoryItem)
def update_asset_inventory_item_assignment(instance, created, raw=False, **kwargs):
    try:
        # will raise RelatedObjectDoesNotExist if not set
        asset = instance.assigned_asset
    except Asset.DoesNotExist:
        return
    # only set if not already
    if getattr(asset, asset.kind) == instance:
        asset.snapshot()
        setattr(asset, asset.kind, instance)
        asset.full_clean()
        asset.save()
