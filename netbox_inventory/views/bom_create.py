from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

from netbox.views import generic

from .. import models, forms

__all__ = ('PurchaseCreateBOMView',)

class PurchaseCreateBOMView(generic.ObjectEditView):
    queryset = models.BOM.objects.all()
    form = forms.BOMForm

    def dispatch(self, request, *args, **kwargs):
        self.purchase = get_object_or_404(models.Purchase, pk=kwargs['purchase_id'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_object(self, **kwargs):
        # Override to prevent filtering BOMs by purchase_id and ensure new BOM is created
        return models.BOM()

    def get_extra_context(self, request, instance):
        return {
            'purchase': self.purchase,
            'return_url': self.purchase.get_absolute_url(),
        }

    def post(self, request, *args, **kwargs):
        form = self.form(request.POST)
        if form.is_valid():
            bom = form.save()
            self.purchase.boms.add(bom)
            messages.success(request, f'BOM "{bom.name}" has been added to Purchase "{self.purchase.name}".')
            return redirect(self.purchase.get_absolute_url())
        else:
            messages.error(request, "There was an error creating the BOM.")
        return self.get(request, *args, **kwargs)