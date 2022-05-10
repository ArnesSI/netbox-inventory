import logging
from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils.html import escape
from django.utils.safestring import mark_safe

from dcim.models import Device, InventoryItem, Module
from extras.signals import clear_webhooks
from netbox.views import generic
from utilities.exceptions import PermissionsViolation
from utilities.forms import restrict_form_fields
from .. import filtersets, forms, models, tables

__all__ = (
    'AssetView',
    'AssetListView',
    'AssetEditView',
    'AssetDeleteView',
    'AssetBulkImportView',
    'AssetBulkEditView',
    'AssetBulkDeleteView',
    'AssetAssignView',
    'AssetCreateHardwareView',
)


class AssetView(generic.ObjectView):
    queryset = models.Asset.objects.all()


class AssetListView(generic.ObjectListView):
    queryset = models.Asset.objects.all()
    table = tables.AssetTable
    filterset = filtersets.AssetFilterSet
    filterset_form = forms.AssetFilterForm


class AssetEditView(generic.ObjectEditView):
    queryset = models.Asset.objects.all()
    form = forms.AssetForm


class AssetDeleteView(generic.ObjectDeleteView):
    queryset = models.Asset.objects.all()


class AssetBulkImportView(generic.BulkImportView):
    queryset = models.Asset.objects.all()
    table = tables.AssetTable
    model_form = forms.AssetCSVForm


class AssetBulkEditView(generic.BulkEditView):
    queryset = models.Asset.objects.all()
    filterset = filtersets.AssetFilterSet
    table = tables.AssetTable
    form = forms.AssetBulkEditForm


class AssetBulkDeleteView(generic.BulkDeleteView):
    queryset = models.Asset.objects.all()
    table = tables.AssetTable


class AssetAssignView(generic.ObjectEditView):
    queryset = models.Asset.objects.all()
    template_name = 'netbox_inventory/asset_assign.html'

    def dispatch(self, request, *args, **kwargs):
        # Set the form class based on the type of hardware being assigned
        obj = self.get_object(**kwargs)
        self.form = {
            'device': forms.AssetAssignDeviceForm,
            'module': forms.AssetAssignModuleForm,
            'inventoryitem': forms.AssetAssignInventoryItemForm,
        }[obj.kind]
        return super().dispatch(request, *args, **kwargs)


class AssetCreateHardwareView(generic.ObjectEditView):
    """
        Creates device/module/inventory item and assigns it to selected asset

        Dynamically sets queryset, template and form, based on asset.kind

        Creates a new device/module/inventory item instance and assigns its
        attr assigned_asset so it is accessible in form.

    """
    queryset = models.Asset.objects.all()
    default_return_url = 'plugins:netbox_inventory:asset_list'

    def get_object(self, **kwargs):
        if self.asset.kind == 'device':
            return Device(assigned_asset=self.asset)
        elif self.asset.kind == 'module':
            return Module(assigned_asset=self.asset)
        elif self.asset.kind == 'inventoryitem':
            return InventoryItem(assigned_asset=self.asset)

    def dispatch(self, request, *args, **kwargs):
        # Set the form class based on the type of hardware being created
        self.asset = models.Asset.objects.get(**kwargs)
        if self.asset.kind == 'device':
            self.queryset = Device.objects.all()
            self.form = forms.AssetCreateDeviceForm
            self.template_name = 'netbox_inventory/asset_create_device.html'
        elif self.asset.kind == 'module':
            self.queryset = Module.objects.all()
            self.form = forms.AssetCreateModuleForm
            self.template_name = 'netbox_inventory/asset_create_module.html'
        elif self.asset.kind == 'inventoryitem':
            self.queryset = InventoryItem.objects.all()
            self.form = forms.AssetCreateInventoryItemForm
            self.template_name = 'netbox_inventory/asset_create_inventoryitem.html'
        ret =  super().dispatch(request, *args, **kwargs)
        self._permission_action = 'add'
        return ret

    def get_extra_context(self, request, instance):
        context = super().get_extra_context(request, instance)
        context['asset'] = self.asset
        return context

    def post(self, request, *args, **kwargs):
        """
        Reimplements netbox.generic.ObjectEditView.post()

        Assigns created obj to asset after obj saved
        """
        logger = logging.getLogger('netbox.netbox_inventory.views.AssetCreateHardwareView')
        obj = self.get_object(**kwargs)

        # Take a snapshot for change logging (if editing an existing object)
        if obj.pk and hasattr(obj, 'snapshot'):
            obj.snapshot()

        obj = self.alter_object(obj, request, args, kwargs)
        
        form = self.form(data=request.POST, files=request.FILES, instance=obj)
        restrict_form_fields(form, request.user)

        if form.is_valid():
            logger.debug("Form validation was successful")

            try:
                with transaction.atomic():
                    object_created = form.instance.pk is None
                    obj = form.save()

                    # Check that the new object conforms with any assigned object-level permissions
                    if not self.queryset.filter(pk=obj.pk).first():
                        raise PermissionsViolation()

                    # assign assset to new object
                    self.asset.snapshot()
                    setattr(self.asset, self.asset.kind, obj)
                    self.asset.full_clean()
                    self.asset.save()

                msg = '{} {}'.format(
                    'Created' if object_created else 'Modified',
                    self.queryset.model._meta.verbose_name
                )
                logger.info(f"{msg} {obj} (PK: {obj.pk})")
                if hasattr(obj, 'get_absolute_url'):
                    msg = '{} <a href="{}">{}</a>'.format(msg, obj.get_absolute_url(), escape(obj))
                else:
                    msg = '{} {}'.format(msg, escape(obj))
                messages.success(request, mark_safe(msg))

                return_url = self.get_return_url(request, obj)

                return redirect(return_url)

            except PermissionsViolation:
                msg = "Object save failed due to object-level permissions violation"
                logger.debug(msg)
                form.add_error(None, msg)
                clear_webhooks.send(sender=self)

        else:
            logger.debug("Form validation failed")

        return render(request, self.template_name, {
            'object': obj,
            'form': form,
            'return_url': self.get_return_url(request, obj),
            **self.get_extra_context(request, obj),
        })
