from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from netbox.views import generic
from .. import models, forms

class DeliveryCreatePurchaseView(generic.ObjectEditView):
    queryset = models.Purchase.objects.all()
    form = forms.PurchaseForm

    def dispatch(self, request, *args, **kwargs):
        self.delivery = get_object_or_404(models.Delivery, pk=kwargs['delivery_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, **kwargs):
        # Override to ensure a new Purchase is created
        return models.Purchase()

    def get_extra_context(self, request, instance):
        return {
            'delivery': self.delivery,
            'return_url': self.delivery.get_absolute_url(),
        }

    def post(self, request, *args, **kwargs):
        form = self.form(request.POST)
        if form.is_valid():
            purchase = form.save()
            self.delivery.purchases.add(purchase)  # Associate the new Purchase with the Delivery
            messages.success(request, f'Purchase "{purchase.name}" has been added to Delivery "{self.delivery.name}".')
            return redirect(self.delivery.get_absolute_url())
        else:
            messages.error(request, "There was an error creating the Purchase.")
        return self.get(request, *args, **kwargs)