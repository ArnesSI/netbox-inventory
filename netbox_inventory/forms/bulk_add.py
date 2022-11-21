from django import forms

from utilities.forms import BootstrapMixin

__all__ = (
    'AssetBulkAddForm',
)


class AssetBulkAddForm(BootstrapMixin, forms.Form):
    """ Form for creating multiple Assets by count """
    count = forms.IntegerField(
        min_value=1,
        required=True,
        help_text='How many assets to create',
    )
