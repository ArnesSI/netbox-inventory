import django_tables2 as tables
from django.db.models.functions import Coalesce
from django.utils.translation import gettext_lazy as _

from dcim.tables import (
    DeviceTypeTable,
    LocationTable,
    ModuleTypeTable,
    RackTypeTable,
)
from netbox.tables import NetBoxTable, PrimaryModelTable, columns
from tenancy.tables import ContactsColumnMixin
from utilities.tables import register_table_column

from .models import *
from .template_content import WARRANTY_PROGRESSBAR

__all__ = (
    'AssetTable',
    'AuditFlowPageAssignmentTable',
    'AuditFlowPageTable',
    'AuditFlowTable',
    'AuditTrailTable',
    'SupplierTable',
    'PurchaseTable',
    'DeliveryTable',
    'InventoryItemTypeTable',
    'InventoryItemGroupTable',
)


#
# Assets
#


class InventoryItemGroupTable(PrimaryModelTable):
    name = columns.MPTTColumn(
        linkify=True,
    )
    asset_count = columns.LinkedCountColumn(
        viewname='plugins:netbox_inventory:asset_list',
        url_params={'inventoryitem_group_id': 'pk'},
        verbose_name='Assets',
    )
    inventoryitem_type_count = columns.LinkedCountColumn(
        viewname='plugins:netbox_inventory:inventoryitemtype_list',
        url_params={'inventoryitem_group_id': 'pk'},
        verbose_name='Inventory Item Types',
    )
    tags = columns.TagColumn()

    class Meta(NetBoxTable.Meta):
        model = InventoryItemGroup
        fields = (
            'pk',
            'id',
            'name',
            'description',
            'comments',
            'tags',
            'created',
            'last_updated',
            'actions',
            'asset_count',
            'inventoryitem_type_count',
        )
        default_columns = (
            'name',
            'asset_count',
            'inventoryitem_type_count',
        )


class InventoryItemTypeTable(PrimaryModelTable):
    manufacturer = tables.Column(
        linkify=True,
    )
    model = tables.Column(
        linkify=True,
    )
    inventoryitem_group = tables.Column(
        linkify=True,
    )
    asset_count = columns.LinkedCountColumn(
        viewname='plugins:netbox_inventory:asset_list',
        url_params={'inventoryitem_type_id': 'pk'},
        verbose_name='Assets',
    )
    tags = columns.TagColumn()

    class Meta(NetBoxTable.Meta):
        model = InventoryItemType
        fields = (
            'pk',
            'id',
            'manufacturer',
            'model',
            'slug',
            'part_number',
            'inventoryitem_group',
            'description',
            'comments',
            'tags',
            'created',
            'last_updated',
            'actions',
            'asset_count',
        )
        default_columns = (
            'manufacturer',
            'model',
            'asset_count',
        )


class AssetTable(PrimaryModelTable):
    name = tables.Column(
        linkify=True,
    )
    serial = tables.Column(
        linkify=True,
    )
    kind = tables.Column(
        accessor='get_kind_display',
        orderable=False,
    )
    manufacturer = tables.Column(
        accessor='hardware_type__manufacturer',
        linkify=True,
    )
    hardware_type = tables.Column(
        linkify=True,
        verbose_name='Hardware Type',
    )
    inventoryitem_group = tables.Column(
        accessor='inventoryitem_type__inventoryitem_group',
        linkify=True,
        verbose_name='Inventory Item Group',
    )
    status = columns.ChoiceFieldColumn()
    hardware = tables.Column(
        linkify=True,
        order_by=('device', 'module'),
    )
    hardware_role = tables.Column(
        accessor=columns.Accessor('hardware__role'),
        linkify=True,
        verbose_name='Hardware Role',
    )
    installed_site = tables.Column(
        linkify=True,
        verbose_name='Installed Site',
    )
    installed_location = tables.Column(
        linkify=True,
        verbose_name='Installed Location',
    )
    installed_rack = tables.Column(
        linkify=True,
        verbose_name='Installed Rack',
    )
    installed_device = tables.Column(
        linkify=True,
        verbose_name='Installed Device',
    )
    tenant = tables.Column(
        linkify=True,
    )
    contact = tables.Column(
        linkify=True,
    )
    storage_location = tables.Column(
        linkify=True,
    )
    owning_tenant = tables.Column(
        linkify=True,
    )
    supplier = tables.Column(
        accessor='purchase__supplier',
        linkify=True,
    )
    purchase = tables.Column(
        linkify=True,
    )
    delivery = tables.Column(
        linkify=True,
    )
    purchase_date = columns.DateColumn(
        accessor='purchase__date',
        verbose_name='Purchase Date',
    )
    delivery_date = columns.DateColumn(
        accessor='delivery__date',
        verbose_name='Delivery Date',
    )
    current_site = tables.Column(
        linkify=True,
        verbose_name='Current Site',
        orderable=False,
    )
    current_location = tables.Column(
        linkify=True,
        verbose_name='Current Location',
        orderable=False,
    )
    warranty_progress = columns.TemplateColumn(
        template_code=WARRANTY_PROGRESSBAR,
        order_by='warranty_end',
        # orderable=False,
        verbose_name='Warranty remaining',
    )
    tags = columns.TagColumn()
    actions = columns.ActionsColumn(
        extra_buttons="""
            {% if record.hardware %}
            <a href="#" class="btn btn-sm btn-outline-dark disabled">
                <i class="mdi mdi-vector-difference-ba" aria-hidden="true"></i>
            </a>
            {% else %}
            <a href="{% url 'plugins:netbox_inventory:asset_'|add:record.kind|add:'_create' %}?asset_id={{ record.pk }}" class="btn btn-sm btn-green" title="Create hardware from asset">
                <i class="mdi mdi-vector-difference-ba"></i>
            </a>
            {% endif %}
            <a href="{% url 'plugins:netbox_inventory:asset_assign' record.pk %}" class="btn btn-sm btn-orange" title="Edit hardware assignment">
                <i class="mdi mdi-vector-link"></i>
            </a>
        """
    )

    def order_manufacturer(self, queryset, is_descending):
        queryset = queryset.annotate(
            manufacturer=Coalesce(
                'device_type__manufacturer',
                'module_type__manufacturer',
                'inventoryitem_type__manufacturer',
                'rack_type__manufacturer',
            )
        ).order_by(
            ('-' if is_descending else '') + 'manufacturer',
            ('-' if is_descending else '') + 'serial',
        )
        return (queryset, True)

    def order_hardware_type(self, queryset, is_descending):
        queryset, _ = self.order_manufacturer(queryset, is_descending)
        queryset = queryset.annotate(
            model=Coalesce(
                'device_type__model',
                'module_type__model',
                'inventoryitem_type__model',
                'rack_type__model',
            )
        ).order_by(
            ('-' if is_descending else '') + 'manufacturer',
            ('-' if is_descending else '') + 'model',
            ('-' if is_descending else '') + 'serial',
        )
        return (queryset, True)

    def order_hardware(self, queryset, is_descending):
        queryset = queryset.annotate(
            hw=Coalesce(
                'device__name',
                'module__device__name',
                'inventoryitem__device__name',
                'rack__name',
            )
        ).order_by(
            ('-' if is_descending else '') + 'hw',
            ('-' if is_descending else '') + 'module__module_bay',
            ('-' if is_descending else '') + 'serial',
        )
        return (queryset, True)

    def order_hardware_role(self, queryset, is_descending):
        queryset = queryset.annotate(
            role_name=Coalesce(
                'device__role__name',
                'inventoryitem__role__name',
                'rack__role__name',
            )
        ).order_by(
            ('-' if is_descending else '') + 'role_name',
            ('-' if is_descending else '') + 'serial',
        )
        return (queryset, True)

    def _order_annotate_installed(self, queryset):
        return queryset.annotate(
            site_name=Coalesce(
                'device__site__name',
                'module__device__site__name',
                'inventoryitem__device__site__name',
                'rack__site__name',
            ),
            location_name=Coalesce(
                'device__location__name',
                'module__device__location__name',
                'inventoryitem__device__location__name',
                'rack__location__name',
            ),
            rack_name=Coalesce(
                'device__rack__name',
                'module__device__rack__name',
                'inventoryitem__device__rack__name',
                'rack__name',
            ),
            device_name=Coalesce(
                'device__name', 'module__device__name', 'inventoryitem__device__name'
            ),
        )

    def order_installed_site(self, queryset, is_descending):
        queryset = self._order_annotate_installed(queryset).order_by(
            ('-' if is_descending else '') + 'site_name',
            ('-' if is_descending else '') + 'device_name',
            ('-' if is_descending else '') + 'module__module_bay',
            ('-' if is_descending else '') + 'serial',
        )
        return (queryset, True)

    def order_installed_location(self, queryset, is_descending):
        queryset = self._order_annotate_installed(queryset).order_by(
            ('-' if is_descending else '') + 'site_name',
            ('-' if is_descending else '') + 'location_name',
            ('-' if is_descending else '') + 'device_name',
            ('-' if is_descending else '') + 'module__module_bay',
            ('-' if is_descending else '') + 'serial',
        )
        return (queryset, True)

    def order_installed_rack(self, queryset, is_descending):
        queryset = self._order_annotate_installed(queryset).order_by(
            ('-' if is_descending else '') + 'site_name',
            ('-' if is_descending else '') + 'location_name',
            ('-' if is_descending else '') + 'rack_name',
            ('-' if is_descending else '') + 'device_name',
            ('-' if is_descending else '') + 'module__module_bay',
            ('-' if is_descending else '') + 'serial',
        )
        return (queryset, True)

    def order_installed_device(self, queryset, is_descending):
        queryset = self._order_annotate_installed(queryset).order_by(
            ('-' if is_descending else '') + 'device_name',
            ('-' if is_descending else '') + 'module__module_bay',
            ('-' if is_descending else '') + 'serial',
        )
        return (queryset, True)

    class Meta(NetBoxTable.Meta):
        model = Asset
        fields = (
            'pk',
            'id',
            'name',
            'asset_tag',
            'serial',
            'status',
            'kind',
            'manufacturer',
            'hardware_type',
            'inventoryitem_group',
            'hardware',
            'hardware_role',
            'installed_site',
            'installed_location',
            'installed_rack',
            'installed_device',
            'tenant',
            'contact',
            'storage_site',
            'storage_location',
            'current_site',
            'current_location',
            'owning_tenant',
            'supplier',
            'purchase',
            'delivery',
            'purchase_date',
            'delivery_date',
            'warranty_start',
            'warranty_end',
            'warranty_progress',
            'description',
            'comments',
            'tags',
            'created',
            'last_updated',
            'actions',
        )
        default_columns = (
            'id',
            'name',
            'serial',
            'kind',
            'manufacturer',
            'hardware_type',
            'asset_tag',
            'status',
            'hardware',
            'tags',
        )


#
# Deliveries
#


class SupplierTable(ContactsColumnMixin, PrimaryModelTable):
    name = tables.Column(
        linkify=True,
    )
    purchase_count = columns.LinkedCountColumn(
        viewname='plugins:netbox_inventory:purchase_list',
        url_params={'supplier_id': 'pk'},
        verbose_name='Purchases',
    )
    delivery_count = columns.LinkedCountColumn(
        viewname='plugins:netbox_inventory:delivery_list',
        url_params={'supplier_id': 'pk'},
        verbose_name='Deliveries',
    )
    asset_count = columns.LinkedCountColumn(
        viewname='plugins:netbox_inventory:asset_list',
        url_params={'supplier_id': 'pk'},
        verbose_name='Assets',
    )
    tags = columns.TagColumn()

    class Meta(NetBoxTable.Meta):
        model = Supplier
        fields = (
            'pk',
            'id',
            'name',
            'slug',
            'description',
            'comments',
            'contacts',
            'purchase_count',
            'delivery_count',
            'asset_count',
            'tags',
            'created',
            'last_updated',
            'actions',
        )
        default_columns = (
            'name',
            'asset_count',
        )


class PurchaseTable(PrimaryModelTable):
    supplier = tables.Column(
        linkify=True,
    )
    name = tables.Column(
        linkify=True,
    )
    status = columns.ChoiceFieldColumn()
    delivery_count = columns.LinkedCountColumn(
        viewname='plugins:netbox_inventory:delivery_list',
        url_params={'purchase_id': 'pk'},
        verbose_name='Deliveries',
    )
    asset_count = columns.LinkedCountColumn(
        viewname='plugins:netbox_inventory:asset_list',
        url_params={'purchase_id': 'pk'},
        verbose_name='Assets',
    )
    tags = columns.TagColumn()

    class Meta(NetBoxTable.Meta):
        model = Purchase
        fields = (
            'pk',
            'id',
            'name',
            'supplier',
            'status',
            'date',
            'description',
            'comments',
            'delivery_count',
            'asset_count',
            'tags',
            'created',
            'last_updated',
            'actions',
        )
        default_columns = (
            'name',
            'supplier',
            'date',
            'asset_count',
        )


class DeliveryTable(PrimaryModelTable):
    supplier = tables.Column(
        accessor=columns.Accessor('purchase__supplier'),
        linkify=True,
    )
    purchase = tables.Column(
        linkify=True,
    )
    date = columns.DateColumn(
        verbose_name='Delivery Date',
    )
    purchase_date = columns.DateColumn(
        accessor=columns.Accessor('purchase__date'),
        verbose_name='Purchase Date',
    )
    receiving_contact = tables.Column(
        linkify=True,
    )
    name = tables.Column(
        linkify=True,
    )
    asset_count = columns.LinkedCountColumn(
        viewname='plugins:netbox_inventory:asset_list',
        url_params={'delivery_id': 'pk'},
        verbose_name='Assets',
    )
    tags = columns.TagColumn()

    class Meta(NetBoxTable.Meta):
        model = Delivery
        fields = (
            'pk',
            'id',
            'name',
            'purchase',
            'supplier',
            'date',
            'purchase_date',
            'receiving_contact',
            'description',
            'comments',
            'asset_count',
            'tags',
            'created',
            'last_updated',
            'actions',
        )
        default_columns = (
            'name',
            'purchase',
            'date',
            'asset_count',
        )


#
# Audit
#


class BaseFlowTable(PrimaryModelTable):
    """
    Internal base table class for audit flow models.
    """

    name = tables.Column(
        linkify=True,
    )
    object_type = columns.ContentTypeColumn(
        verbose_name=_('Object Type'),
    )

    class Meta(NetBoxTable.Meta):
        fields = (
            'pk',
            'id',
            'name',
            'description',
            'object_type',
            'object_filter',
            'comments',
            'actions',
        )
        default_columns = (
            'name',
            'object_type',
        )


class AuditFlowPageTable(BaseFlowTable):
    class Meta(BaseFlowTable.Meta):
        model = AuditFlowPage


class AuditFlowTable(BaseFlowTable):
    enabled = columns.BooleanColumn()

    class Meta(BaseFlowTable.Meta):
        model = AuditFlow
        fields = BaseFlowTable.Meta.fields + ('enabled',)
        default_columns = BaseFlowTable.Meta.default_columns + ('enabled',)


class AuditFlowPageAssignmentTable(NetBoxTable):
    flow = tables.Column(
        linkify=True,
    )
    page = tables.Column(
        linkify=True,
    )

    actions = columns.ActionsColumn(
        actions=(
            'edit',
            'delete',
        ),
    )

    class Meta(NetBoxTable.Meta):
        model = AuditFlowPageAssignment
        fields = (
            'pk',
            'id',
            'flow',
            'page',
            'weight',
            'actions',
        )
        default_columns = (
            'flow',
            'page',
            'weight',
        )


class AuditTrailSourceTable(PrimaryModelTable):
    name = tables.Column(
        linkify=True,
    )
    tags = columns.TagColumn()

    class Meta(NetBoxTable.Meta):
        model = AuditTrailSource
        fields = (
            'pk',
            'id',
            'name',
            'description',
            'tags',
            'comments',
            'actions',
        )
        default_columns = ('name',)


class AuditTrailTable(NetBoxTable):
    object_type = columns.ContentTypeColumn(
        verbose_name=_('Object Type'),
    )
    object = tables.Column(
        verbose_name=_('Object'),
        linkify=True,
        orderable=False,
    )
    source = tables.Column(
        linkify=True,
    )
    created = columns.DateTimeColumn(
        verbose_name=_('Time'),
        timespec='minutes',
    )
    actions = columns.ActionsColumn(
        actions=('delete',),
    )

    # Access the audit user via the first associated object change.
    auditor_user = tables.Column(
        accessor=tables.A('object_changes__first__user_name'),
        verbose_name=_('Auditor Username'),
        orderable=False,
    )
    auditor_full_name = tables.Column(
        accessor=tables.A('object_changes__first__user__get_full_name'),
        verbose_name=_('Auditor Full Name'),
        linkify=True,
        orderable=False,
    )

    class Meta(NetBoxTable.Meta):
        model = AuditTrail
        fields = (
            'pk',
            'id',
            'object_type',
            'object',
            'auditor_user',
            'auditor_full_name',
            'source',
            'created',
            'last_changed',
            'actions',
        )
        default_columns = (
            'pk',
            'created',
            'object_type',
            'object',
            'auditor_user',
            'auditor_full_name',
            'source',
        )


# ========================
# DCIM model table columns
# ========================

asset_count = columns.LinkedCountColumn(
    viewname='plugins:netbox_inventory:asset_list',
    url_params={'device_type_id': 'pk'},
    verbose_name=_('Asset Count'),
    accessor='assets__count',
    orderable=False,
)

register_table_column(asset_count, 'assets', DeviceTypeTable)


asset_count = columns.LinkedCountColumn(
    viewname='plugins:netbox_inventory:asset_list',
    url_params={'module_type_id': 'pk'},
    verbose_name=_('AsseAsset Countts'),
    accessor='assets__count',
    orderable=False,
)

register_table_column(asset_count, 'assets', ModuleTypeTable)


asset_count = columns.LinkedCountColumn(
    viewname='plugins:netbox_inventory:asset_list',
    url_params={'rack_type_id': 'pk'},
    verbose_name=_('Asset Count'),
    accessor='assets__count',
    orderable=False,
)

register_table_column(asset_count, 'assets', RackTypeTable)


asset_count = columns.LinkedCountColumn(
    viewname='plugins:netbox_inventory:asset_list',
    url_params={'storage_location_id': 'pk'},
    verbose_name=_('Asset Count'),
    # accessor='assets__count',
    accessor=tables.A('assets__count_with_children'),
    orderable=False,
)

register_table_column(asset_count, 'assets', LocationTable)
