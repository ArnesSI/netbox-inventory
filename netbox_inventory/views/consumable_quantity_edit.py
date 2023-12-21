from django.shortcuts import redirect

from dcim.models import Device, InventoryItem, Module
from netbox.views import generic
from .. import forms, models
from ..models import Consumable

__all__ = (
    'ConsumableIncrementView',
    'ConsumableDecrementView',
)


class ConsumableIncrementView(generic.ObjectEditView):
    queryset = models.Consumable.objects.all()
    template_name = 'netbox_inventory/consumable_increment.html'
    form = forms.consumable.ConsumableIncrementForm
    
    def post(self, request, *args, **kwargs):
        # Override post so we can redirect back to the main consumables page
        ret = super().post(request, *args, **kwargs)

        return redirect('/plugins/inventory/consumable/')


class ConsumableDecrementView(generic.ObjectEditView):
    queryset = models.Consumable.objects.all()
    template_name = 'netbox_inventory/consumable_decrement.html'
    form = forms.consumable.ConsumableDecrementForm

    def post(self, request, *args, **kwargs):
        # Override post so we can redirect back to the main consumables page
        ret = super().post(request, *args, **kwargs)

        return redirect('/plugins/inventory/consumable/')

