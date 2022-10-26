####
#### Taken from https://github.com/auroraresearchlab/netbox-dns/blob/main/netbox_dns/tests/custom.py
####
#### Makes it so Netbox test utils work with plugins
####

from django.urls import reverse

from utilities.testing.api import APITestCase as NetBoxAPITestCase
from utilities.testing.views import ModelViewTestCase as NetBoxModelViewTestCase


class ModelViewTestCase(NetBoxModelViewTestCase):
    """
    Customized ModelViewTestCase for work with plugins
    """

    def _get_base_url(self):
        """
        Return the base format for a URL for the test's model. Override this to test for a model which belongs
        to a different app (e.g. testing Interfaces within the virtualization app).
        """
        return (
            f"plugins:{self.model._meta.app_label}:{self.model._meta.model_name}_{{}}"
        )


class APITestCase(NetBoxAPITestCase):
    """
    Customized APITestCase for work with plugins
    """

    def _get_detail_url(self, instance):
        viewname = f"plugins-api:{self._get_view_namespace()}:{instance._meta.model_name}-detail"
        return reverse(viewname, kwargs={"pk": instance.pk})

    def _get_list_url(self):
        viewname = f"plugins-api:{self._get_view_namespace()}:{self.model._meta.model_name}-list"
        return reverse(viewname)
