from django import template
from django.urls import NoReverseMatch, reverse

from utilities.views import get_viewname

__all__ = (
    'bulk_scan_button',
)

register = template.Library()

@register.inclusion_tag('netbox_inventory/buttons/bulk_scan.html', takes_context=True)
def bulk_scan_button(context, model, action='bulk_scan', query_params=None):
    try:
        url = reverse(get_viewname(model, action))
        if query_params:
            url = f'{url}?{query_params.urlencode()}'
    except NoReverseMatch:
        url = None

    return {
        'htmx_navigation': context.get('htmx_navigation'),
        'url': url,
    }
