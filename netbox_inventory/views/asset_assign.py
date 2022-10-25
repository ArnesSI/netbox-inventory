from netbox.views import generic

from ..forms.assign import *
from ..models import Asset

__all__ = (
    'AssetAssignView',
)


class AssetAssignView(generic.ObjectEditView):
    queryset = Asset.objects.all()
    template_name = 'netbox_inventory/asset_assign.html'

    def dispatch(self, request, *args, **kwargs):
        # Set the form class based on the type of hardware being assigned
        obj = self.get_object(**kwargs)
        self.form = {
            'device': AssetDeviceAssignForm,
            'module': AssetModuleAssignForm,
            'inventoryitem': AssetInventoryItemAssignForm,
        }[obj.kind]
        return super().dispatch(request, *args, **kwargs)
