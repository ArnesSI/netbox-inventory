from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

from netbox.views import generic

from .. import models, tables

__all__ = ('AssetBulkAssignView',)

class AssetBulkAssignView(generic.ObjectListView):
    queryset = models.Asset.objects.all()
    table = tables.AssetTable
    template_name = 'netbox_inventory/asset_bulk_assign.html'

    def get_extra_context(self, request):
        purchase_id = request.GET.get('purchase_id')
        purchase_name = request.GET.get('purchase_name')
        return {
            'purchase_id': purchase_id,
            'purchase_name': purchase_name,
        }
    
    def post(self, request, *args, **kwargs):
        purchase_id = request.GET.get('purchase_id')
        purchase_name = request.GET.get('purchase_name')
        asset_ids = request.POST.getlist('pk')

        if not purchase_id or not asset_ids:
            messages.error(request, "No purchase or assets selected.")
            return redirect(f"{request.path}?purchase_id={purchase_id}&purchase_name={purchase_name}")

        try:
            purchase = models.Purchase.objects.get(pk=purchase_id)
        except models.Purchase.DoesNotExist:
            messages.error(request, "Invalid purchase ID.")
            return redirect(f"{request.path}?purchase_id={purchase_id}&purchase_name={purchase_name}")

        assets = models.Asset.objects.filter(pk__in=asset_ids)
        assets.update(purchase=purchase)

        messages.success(request, f"Successfully assigned {assets.count()} assets to purchase {purchase.name}.")
        return redirect(reverse('plugins:netbox_inventory:purchase', args=[purchase_id]))