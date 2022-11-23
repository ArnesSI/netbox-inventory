import logging

from django.dispatch import receiver
from django.db.models.signals import pre_save, pre_delete

from dcim.models import Device, Module, InventoryItem
from utilities.exceptions import AbortRequest
from .models import Asset
from .utils import get_plugin_setting, get_status_for


logger = logging.getLogger('netbox.netbox_inventory.signals')


@receiver(pre_save, sender=Device)
@receiver(pre_save, sender=Module)
@receiver(pre_save, sender=InventoryItem)
def prevent_update_serial_asset_tag(instance, **kwargs):
    """
    When a hardware (Device, Module or InventoryItem) has an Asset assigned and
    user changes serial or asset_tag on hardware, prevent that change
    and inform that change must be made on Asset instance instead.
    
    Only enforces if `sync_hardware_serial_asset_tag` setting is true.
    """
    try:
        # will raise RelatedObjectDoesNotExist if not set
        asset = instance.assigned_asset
    except Asset.DoesNotExist:
        return
    if not get_plugin_setting('sync_hardware_serial_asset_tag'):
        # don't enforce if sync not enabled
        return
    if asset.serial != instance.serial or asset.asset_tag != instance.asset_tag:
        raise AbortRequest(f'Cannot change {asset.kind} serial and asset tag if asset is asigned. Please update via inventory > asset instead.')


@receiver(pre_delete, sender=Device)
@receiver(pre_delete, sender=Module)
@receiver(pre_delete, sender=InventoryItem)
def free_assigned_asset(instance, **kwargs):
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
