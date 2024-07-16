from django.db.models.functions import Coalesce
import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from netbox.tables import columns, NetBoxTable
from tenancy.tables import ContactsColumnMixin
from .models import Asset, Delivery, InventoryItemType, InventoryItemGroup, Purchase, Supplier
from .template_content import WARRANTY_PROGRESSBAR

from dcim.tables import DeviceTypeTable, ModuleTypeTable
from utilities.tables import register_table_column

__all__ = (
    'AssetTable',
    'SupplierTable',
    'PurchaseTable',
    'DeliveryTable',
    'InventoryItemTypeTable',
    'InventoryItemGroupTable',
)


class AssetTable(NetBoxTable):
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
    owner = tables.Column(
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
    )
    current_location = tables.Column(
        linkify=True,
        verbose_name='Current Location',
    )
    warranty_progress = columns.TemplateColumn(
        template_code=WARRANTY_PROGRESSBAR,
        order_by='warranty_end',
        #orderable=False,
        verbose_name='Warranty remaining',
    )
    comments = columns.MarkdownColumn()
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
                'device_type__model', 'module_type__model', 'inventoryitem_type__model'
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
                'device__name', 'module__device__name', 'inventoryitem__device__name'
            )
        ).order_by(
            ('-' if is_descending else '') + 'hw',
            ('-' if is_descending else '') + 'module__module_bay',
            ('-' if is_descending else '') + 'serial',
        )
        return (queryset, True)
    
    def _order_annotate_installed(self, queryset):
        return queryset.annotate(
            site_name=Coalesce(
                'device__site__name', 'module__device__site__name', 'inventoryitem__device__site__name'
            ),
            location_name=Coalesce(
                'device__location__name', 'module__device__location__name', 'inventoryitem__device__location__name'
            ),
            rack_name=Coalesce(
                'device__rack__name', 'module__device__rack__name', 'inventoryitem__device__rack__name'
            ),
            device_name=Coalesce(
                'device__name', 'module__device__name', 'inventoryitem__device__name'
            )
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
            'owner',
            'supplier',
            'purchase',
            'delivery',
            'purchase_date',
            'delivery_date',
            'warranty_start',
            'warranty_end',
            'warranty_progress',
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


class SupplierTable(ContactsColumnMixin, NetBoxTable):
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
    comments = columns.MarkdownColumn()
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


class PurchaseTable(NetBoxTable):
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
    comments = columns.MarkdownColumn()
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


class DeliveryTable(NetBoxTable):
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
    comments = columns.MarkdownColumn()
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


class InventoryItemTypeTable(NetBoxTable):
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
    comments = columns.MarkdownColumn()
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


class InventoryItemGroupTable(NetBoxTable):
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
    comments = columns.MarkdownColumn()
    tags = columns.TagColumn()

    class Meta(NetBoxTable.Meta):
        model = InventoryItemGroup
        fields = (
            'pk',
            'id',
            'name',
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


# ========================
# DCIM model table columns
# ========================

asset_count = columns.LinkedCountColumn(
    viewname='plugins:netbox_inventory:asset_list',
    url_params={'device_type_id': 'pk'},
    verbose_name=_('Assets'),
    accessor="assets__count",
)

register_table_column(asset_count, 'assets', DeviceTypeTable)


asset_count = columns.LinkedCountColumn(
    viewname='plugins:netbox_inventory:asset_list',
    url_params={'module_type_id': 'pk'},
    verbose_name=_('Assets'),
    accessor="assets__count",
)

register_table_column(asset_count, 'assets', ModuleTypeTable)
