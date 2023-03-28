from dcim.models import Site, Location, Rack
from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from ..models import Asset
from ..tables import AssetTable
from ..filtersets import AssetFilterSet
from ..utils import query_located


class BaseAssetsTab(generic.ObjectChildrenView):
    """
    Shows Assets tab with table of assets located here
    Can be filtered on installed or stored assets or both.
    Accepts query param assets_shown:
    - stored - show currently stored here (storage_location & stored status)
    - installed - show currently in use here (installed as a or into a device)
    - all - show both
    """
    child_model = Asset
    table = AssetTable
    filterset = AssetFilterSet
    tab = ViewTab(
        label='Assets',
        permission='netbox_inventory.view_asset'
    )

    def get_children(self, request, parent):
        """ Returns queryset that populates the table """
        assets_shown = request.GET.get('assets_shown', 'all')
        typ = parent._meta.model.__name__.lower()
        return query_located(
            Asset.objects.all(),
            typ,
            [parent.pk],
            assets_shown
        )

    def get_extra_context(self, request, instance):
        context = super().get_extra_context(request, instance)
        context['assets_shown'] = request.GET.get('assets_shown', 'all')
        return context


@register_model_view(Site, name='inventory_assets', path='assets')
class SiteAssets(BaseAssetsTab):
    queryset = Site.objects.all()
    template_name = "netbox_inventory/tabs/located_assets_site.html"


@register_model_view(Location, name='inventory_assets', path='assets')
class LocationAssets(BaseAssetsTab):
    queryset = Location.objects.all()
    template_name = "netbox_inventory/tabs/located_assets_location.html"

@register_model_view(Rack, name='inventory_assets', path='assets')
class LocationAssets(BaseAssetsTab):
    queryset = Rack.objects.all()
    template_name = "netbox_inventory/tabs/located_assets_rack.html"
