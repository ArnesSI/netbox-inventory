from django import forms


class BigTextWidget(forms.Textarea):
    template_name = "netbox_inventory/widgets/big_text_input.html"

    def __init__(self, attrs=None):
        default_attrs = {
            "class": "font-monospace",
        }
        if attrs:
            default_attrs.update(attrs)

        super().__init__(default_attrs)
