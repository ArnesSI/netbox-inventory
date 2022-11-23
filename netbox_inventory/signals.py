import logging

from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete

from dcim.models import Device, Module, InventoryItem
from .models import Asset
from .utils import get_status_for


logger = logging.getLogger('netbox.netbox_inventory.signals')

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


@receiver(pre_delete, sender=Device)
@receiver(pre_delete, sender=Module)
@receiver(pre_delete, sender=InventoryItem)
def free_assigned_asset(instance, raw=False, **kwargs):
    """
    If a hardware (Device, Module or InventoryItem) has an Asset assigned and
    that hardware is deleted, uspdate Asset.status to stored_status.

    Netbox handles deletion in a DB transaction, so if deletion failes for any
    reason, this status change will also be reverted.
    """
    stored_status = get_status_for('stored')
    if not stored_status:
        return
    try:
        # will raise RelatedObjectDoesNotExist if not set
        asset = instance.assigned_asset
    except Asset.DoesNotExist:
        return
    asset.status = stored_status
    asset.full_clean()
    asset.save()
    logger.info(f'Asset marked as stored {asset}')
