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


class ConsumableDecrementView(generic.ObjectEditView):
    queryset = models.Consumable.objects.all()
    template_name = 'netbox_inventory/consumable_decrement.html'
    form = forms.consumable.ConsumableDecrementForm

