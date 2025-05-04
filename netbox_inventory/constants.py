from django.db.models import Q

AUDITFLOW_OBJECT_TYPE_CHOICES = Q(
    app_label='dcim',
    model__in=(
        'site',
        'location',
        'rack',
    ),
)
