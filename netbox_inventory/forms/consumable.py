import logging

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.forms import IntegerField, Form

from netbox.forms import NetBoxModelForm
from utilities.forms.fields import DynamicModelChoiceField
from ..utils import get_plugin_setting
from ..models import Consumable

__all__ = (
    'ConsumableIncrementForm',
    'ConsumableDecrementForm',
)



logger = logging.getLogger('netbox.netbox_inventory.forms.consumable')

class ConsumableIncrementForm(NetBoxModelForm):
    increment_qty = IntegerField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # remove tags field from form
        self.fields.pop('tags')

    class Meta:
        model = Consumable
        fields = ('increment_qty', )

    def save(self, *args):
        instance = super().save(*args)
        instance.quantity += self.cleaned_data['increment_qty']
        instance.save()
        return instance


class ConsumableDecrementForm(NetBoxModelForm):
    decrement_qty = IntegerField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # remove tags field from form
        self.fields.pop('tags')

    class Meta:
        model = Consumable
        fields = ('decrement_qty', )


    def save(self, *args):
        instance = super().save(*args)
        instance.quantity -= self.cleaned_data['decrement_qty']
        instance.save()
        return instance
