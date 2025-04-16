from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect

from netbox.views import generic

from .. import forms, models

__all__ = (
    'CreateAndAssignView',
    'DeliveryCreatePurchaseView',
    'PurchaseCreateBOMView',
)


class CreateAndAssignView(generic.ObjectEditView):
    """
    A generic view for creating a new object and associating it with a field on a related object.
    """

    related_model = None
    related_field = None
    related_instance = None
    template_name = 'netbox_inventory/create_and_assign.html'

    def dispatch(self, request, *args, **kwargs):
        self.related_instance = get_object_or_404(
            self.related_model, pk=kwargs['related_id']
        )
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, **kwargs):
        # Override to ensure a new object is created
        return self.queryset.model()

    def get_extra_context(self, request, instance):
        return {
            'related_instance': self.related_instance,
            'return_url': self.related_instance.get_absolute_url(),
        }

    def post(self, request, *args, **kwargs):
        form = self.form(request.POST)
        if form.is_valid():
            obj = form.save()
            getattr(self.related_instance, self.related_field).add(obj)
            messages.success(
                request, f'{obj} has been added to {self.related_instance}.'
            )
            return redirect(self.related_instance.get_absolute_url())
        else:
            messages.error(request, 'There was an error creating the object.')
        return self.get(request, *args, **kwargs)


class DeliveryCreatePurchaseView(CreateAndAssignView):
    queryset = models.Purchase.objects.all()
    form = forms.PurchaseForm
    related_model = models.Delivery
    related_field = 'purchases'

    def dispatch(self, request, *args, **kwargs):
        # Map delivery_id to related_id
        kwargs['related_id'] = kwargs.pop('delivery_id', None)
        return super().dispatch(request, *args, **kwargs)

    def get_extra_context(self, request, instance):
        context = super().get_extra_context(request, instance)
        context['object_type'] = 'purchase'
        return context


class PurchaseCreateBOMView(CreateAndAssignView):
    queryset = models.BOM.objects.all()
    form = forms.BOMForm
    related_model = models.Purchase
    related_field = 'boms'

    def dispatch(self, request, *args, **kwargs):
        # Map purchase_id to related_id
        kwargs['related_id'] = kwargs.pop('purchase_id', None)
        return super().dispatch(request, *args, **kwargs)

    def get_extra_context(self, request, instance):
        context = super().get_extra_context(request, instance)
        context['object_type'] = 'BOM'
        return context
