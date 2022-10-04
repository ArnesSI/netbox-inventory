from django.db.models.functions import Coalesce
import django_tables2 as tables

from netbox.tables import columns, NetBoxTable
from .models import Asset, InventoryItemType, Supplier

__all__ = (
    'AssetTable',
    'SupplierTable',
    'InventoryItemTypeTable',
)


class AssetTable(NetBoxTable):
    name = tables.Column(
        linkify=True,
    )
    serial = tables.Column(
        linkify=True,
    )
    kind = tables.Column(
        orderable=False,
    )
    manufacturer = tables.Column(
        accessor='hardware_type__manufacturer',
        verbose_name='Manufacturer',
        linkify=True,
    )
    hardware_type = tables.Column(
        linkify=True,
        verbose_name='Hardware type',
    )
    status = columns.ChoiceFieldColumn()
    hardware = tables.Column(
        linkify=True,
        order_by=('device', 'module'),
    )
    supplier = tables.Column(
        linkify=True,
    )
    tags = columns.TagColumn()
    actions = columns.ActionsColumn(
        extra_buttons="""
            {% if not record.device_id %}
            <a href="{% url 'plugins:netbox_inventory:asset_create' record.pk %}" class="btn btn-sm btn-green" title="Create from asset">
                <i class="mdi mdi-vector-difference-ba"></i>
            </a>
            {% endif %}
            <a href="{% url 'plugins:netbox_inventory:asset_assign' record.pk %}" class="btn btn-sm btn-orange" title="Edit assignment">
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
            'hardware',
            'tenant',
            'contact',
            'storage_location',
            'owner',
            'supplier',
            'order_number',
            'purchase_date',
            'warranty_start',
            'warranty_end',
            'tags',
            'created',
            'last_updated',
            'actions',
        )
        default_columns = (
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


class SupplierTable(NetBoxTable):
    name = tables.Column(
        linkify=True,
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
            'asset_count',
        )


class InventoryItemTypeTable(NetBoxTable):
    manufacturer = tables.Column(
        linkify=True,
    )
    model = tables.Column(
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
            'comments',
            'tags',
            'created',
            'last_updated',
            'actions',
            'asset_count',
        )
        default_columns = (
            'name',
            'manufacturer',
            'model',
            'asset_count',
        )
