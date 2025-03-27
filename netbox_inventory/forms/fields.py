

from django import forms
from django.templatetags.static import static

from . import widgets

class BigTextField(forms.CharField):
    widget = widgets.BigTextWidget
    label = ('Big Text')

    def __init__(self, *, label=label, required=False, **kwargs):
        super().__init__(label=label, required=required, **kwargs)
