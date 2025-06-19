import logging

from django.db.models import Q
from django.db.models.signals import m2m_changed, post_save, pre_delete, pre_save
from django.dispatch import receiver

from dcim.models import Device, InventoryItem, Module, Rack
from utilities.exceptions import AbortRequest

from .models import Asset, Delivery, InventoryItemGroup
from .utils import get_plugin_setting, get_status_for, is_equal_none

logger = logging.getLogger('netbox.netbox_inventory.signals')


@receiver(pre_save, sender=Device)
@receiver(pre_save, sender=Module)
@receiver(pre_save, sender=InventoryItem)
@receiver(pre_save, sender=Rack)
def prevent_update_serial_asset_tag(instance, **kwargs):
    """
    When a hardware (Device, Module, InventoryItem, Rack) has an Asset assigned and
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
    if instance.pk and (
        not is_equal_none(asset.serial, instance.serial)
        or not is_equal_none(asset.asset_tag, instance.asset_tag)
    ):
        raise AbortRequest(
            f'Cannot change {asset.kind} serial and asset tag if asset is assigned. Please update via inventory > asset instead.'
        )


@receiver(pre_delete, sender=Device)
@receiver(pre_delete, sender=Module)
@receiver(pre_delete, sender=InventoryItem)
@receiver(pre_delete, sender=Rack)
def free_assigned_asset(instance, **kwargs):
    """
    If a hardware (Device, Module, InventoryItem, Rack) has an Asset assigned and
    that hardware is deleted, update Asset.status to stored_status.

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
    asset.snapshot()
    asset.status = stored_status
    # also unassign that item from asset
    setattr(asset, asset.kind, None)
    asset.full_clean()
    asset.save(clear_old_hw=False)
    logger.info(f'Asset marked as stored {asset}')


@receiver(post_save, sender=Delivery)
def handle_delivery_purchase_change(instance, created, **kwargs):
    """
    Update child Assets if Delivery Purchase has changed.
    """
    if not created:
        Asset.objects.filter(delivery=instance).update(purchase=instance.purchase)


@receiver(m2m_changed, sender=InventoryItemGroup.device_types.through)
@receiver(m2m_changed, sender=InventoryItemGroup.module_types.through)
@receiver(m2m_changed, sender=InventoryItemGroup.rack_types.through)
@receiver(m2m_changed, sender=InventoryItemGroup.inventoryitem_types.through)
@receiver(m2m_changed, sender=InventoryItemGroup.direct_assets.through)
def update_assigned_assets(sender, instance, action, reverse, model, pk_set, **kwargs):
    """
    After updating device,module... types assigned to group, we need to update
    assets assigned to that group.
    Note: does not handle updating relation in reverse (eg device_type.inventoryitem_groups.set())
    """
    if not reverse and action in ('post_add', 'post_remove', 'post_clear'):
        query = Q(device_type__in=instance.device_types.all())
        query |= Q(module_type__in=instance.module_types.all())
        query |= Q(rack_type__in=instance.rack_types.all())
        query |= Q(inventoryitem_type__in=instance.inventoryitem_types.all())
        indirect_assets = Asset.objects.filter(query)
        instance.assets.set(indirect_assets.union(instance.direct_assets.all()))
