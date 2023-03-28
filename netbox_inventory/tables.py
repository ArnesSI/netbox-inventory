from django.db.models.functions import Coalesce
import django_tables2 as tables

from netbox.tables import columns, NetBoxTable
from tenancy.tables import ContactsColumnMixin
from .models import Asset, InventoryItemType, InventoryItemGroup, Purchase, Supplier

__all__ = (
    'AssetTable',
    'SupplierTable',
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
    purchase_date = columns.DateColumn(
        accessor='purchase__date',
        verbose_name='Purchase Date',
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
            'storage_location',
            'owner',
            'supplier',
            'purchase',
            'purchase_date',
            'warranty_start',
            'warranty_end',
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
            'date',
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
            'supplier',
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
