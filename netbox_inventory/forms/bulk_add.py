from django import forms

from .models import AssetForm


__all__ = (
    'AssetBulkAddForm',
    'AssetBulkAddModelForm',
)


class AssetBulkAddForm(forms.Form):
    """ Form for creating multiple Assets by count """
    count = forms.IntegerField(
        min_value=1,
        required=True,
        help_text='How many assets to create',
    )


class AssetBulkAddModelForm(AssetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['asset_tag'].disabled = True
        self.fields['serial'].disabled = True
