from collections import defaultdict
from itertools import product
from typing import Any
from urllib.parse import urlencode

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import (
    Model,
    OuterRef,
    QuerySet,
    Subquery,
)
from django.forms.models import ModelChoiceField
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import resolve, reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_tables2 import TemplateColumn

from core.models import ObjectType
from dcim.models import Location, Rack, Site
from netbox.plugins import get_plugin_config
from netbox.tables import NetBoxTable
from netbox.views import generic
from utilities.query import dict_to_filter_params
from utilities.views import ViewTab, get_viewname, register_model_view

from .. import filtersets, forms, models, tables

__all__ = (
    'AuditFlowAssignedPagesView',
    'AuditFlowView',
    'AuditFlowListView',
    'AuditFlowEditView',
    'AuditFlowDeleteView',
    'AuditFlowBulkImportView',
    'AuditFlowBulkEditView',
    'AuditFlowBulkDeleteView',
    'AuditFlowRunView',
)


#
# Admin
#


@register_model_view(models.AuditFlow)
class AuditFlowView(generic.ObjectView):
    queryset = models.AuditFlow.objects.all()


@register_model_view(models.AuditFlow, 'pages')
class AuditFlowAssignedPagesView(generic.ObjectChildrenView):
    queryset = models.AuditFlow.objects.all()
    child_model = models.AuditFlowPageAssignment
    table = tables.AuditFlowPageAssignmentTable
    template_name = 'netbox_inventory/auditflow_pages.html'
    tab = ViewTab(
        label=_('Pages'),
        badge=lambda obj: obj.pages.count(),
        permission='netbox_inventory.view_auditflowpage',
        weight=1000,
    )

    def get_children(self, request: HttpRequest, parent: models.AuditFlow) -> QuerySet:
        return parent.assigned_pages.restrict(request.user, 'view')

    def get_table(self, *args, **kwargs):
        table = super().get_table(*args, **kwargs)
        table.columns.hide('flow')
        return table


@register_model_view(models.AuditFlow, 'list', path='', detail=False)
class AuditFlowListView(generic.ObjectListView):
    queryset = models.AuditFlow.objects.all()
    table = tables.AuditFlowTable
    filterset = filtersets.AuditFlowFilterSet
    filterset_form = forms.AuditFlowFilterForm


@register_model_view(models.AuditFlow, 'add', detail=False)
@register_model_view(models.AuditFlow, 'edit')
class AuditFlowEditView(generic.ObjectEditView):
    queryset = models.AuditFlow.objects.all()
    form = forms.AuditFlowForm


@register_model_view(models.AuditFlow, 'delete')
class AuditFlowDeleteView(generic.ObjectDeleteView):
    queryset = models.AuditFlow.objects.all()


@register_model_view(models.AuditFlow, 'bulk_import', path='import', detail=False)
class AuditFlowBulkImportView(generic.BulkImportView):
    queryset = models.AuditFlow.objects.all()
    model_form = forms.AuditFlowImportForm


@register_model_view(models.AuditFlow, 'bulk_edit', path='edit', detail=False)
class AuditFlowBulkEditView(generic.BulkEditView):
    queryset = models.AuditFlow.objects.all()
    filterset = filtersets.AuditFlowFilterSet
    table = tables.AuditFlowTable
    form = forms.AuditFlowBulkEditForm


@register_model_view(models.AuditFlow, 'bulk_delete', path='delete', detail=False)
class AuditFlowBulkDeleteView(generic.BulkDeleteView):
    queryset = models.AuditFlow.objects.all()
    table = tables.AuditFlowTable


#
# Run
#


@register_model_view(models.AuditFlow, 'run')
class AuditFlowRunView(generic.ObjectChildrenView):
    """
    Run an `AuditFlow` for a specific start object (e.g. a specific `Location`).
    """

    queryset = models.AuditFlow.objects.all()
    template_name = 'netbox_inventory/auditflow_run.html'

    def get_required_permission(self):
        return 'netbox_inventory.run_auditflow'

    @staticmethod
    def get_current_page(
        request: HttpRequest,
        parent: models.AuditFlow,
    ) -> models.AuditFlowPageAssignment:
        """
        Get the currently selected `AuditFlowPage` of the `AuditFlow` based on the `tab`
        query parameter. Defaults to the first assigned page.
        """
        assignment_id = request.GET.get('tab')
        if assignment_id:
            return get_object_or_404(parent.assigned_pages, pk=assignment_id)
        return parent.assigned_pages.first()

    @staticmethod
    def get_object_or_raise(
        queryset: QuerySet,
        request: HttpRequest,
        **kwargs,
    ) -> Model:
        """
        Get an object from `queryset` and raise exceptions either if the object can't be
        found or if the `request` user doesn't have permissions to view the object.
        """
        obj = get_object_or_404(queryset, **kwargs)
        if not queryset.restrict(request.user, 'view').contains(obj):
            raise PermissionDenied()
        return obj

    def get_children(self, request: HttpRequest, parent: models.AuditFlow) -> QuerySet:
        # Each AuditFlowPage handles one specific object type. To support different
        # types of objects with this view, dynamically retrieve the object type model
        # and set class properties for use in other methods and templates.
        self.page = self.get_current_page(request, parent)
        self.tab = self.page.pk
        self.child_model = self.page.page.object_type.model_class()

        # Attributes related to displaying the list of child objects are copied from the
        # object's list view. This allows reusing the existing logic and displaying the
        # objects with the preferences defined by the user.
        view = resolve(reverse(get_viewname(self.child_model, 'list'))).func.view_class
        self.table = getattr(view, 'table', None)
        self.filterset = getattr(view, 'filterset', None)

        # Get the flow start object (e.g. a Site or Location) and limit the page object
        # queryset to that limited audit location.
        self.start_object = self.get_object_or_raise(
            parent.get_objects(),
            request,
            pk=request.GET.get('object_id'),
        )
        queryset = self.page.get_objects(self.start_object)

        # If the object list view has a queryset, get a list of lookups to prefetch from
        # it. This should solve possible N+1 query problems, since a custom queryset is
        # created for each audit flow page. This plugin can't know the specifics of each
        # queryset and its optimizations, so it needs to reuse existing optimizations to
        # improve performance.
        view_queryset = getattr(view, 'queryset', None)
        if view_queryset:
            prefetch_lookups = getattr(view_queryset, '_prefetch_related_lookups', ())
            queryset = queryset.prefetch_related(*prefetch_lookups)

        return queryset

    def prep_table_data(
        self,
        request: HttpRequest,
        queryset: QuerySet,
        parent: models.AuditFlow,
    ) -> QuerySet:
        """
        Annotate the `queryset` with `AuditTrail` data if available.
        """
        # Create a timeframe to select applicable audit trails. This allows users to see
        # an item as audited in that timeframe, eliminating duplicate work.
        timeframe = timezone.now() - timezone.timedelta(
            minutes=get_plugin_config('netbox_inventory', 'audit_window'),
        )

        object_type = ObjectType.objects.get_for_model(self.child_model)
        return queryset.annotate(
            audit_trail=Subquery(
                models.AuditTrail.objects.filter(
                    object_type=object_type,
                    object_id=OuterRef('pk'),
                    created__gte=timeframe,
                ).values('id')[:1]
            ),
        )

    def get_table(
        self,
        data: QuerySet,
        request: HttpRequest,
        bulk_actions: bool = True,
    ) -> NetBoxTable:
        # Extend the default object table with an additional column for marking objects
        # as seen/unseen and viewing their current audit trail status.
        extra_columns = [
            (
                'audit_trail_seen',
                TemplateColumn(
                    template_name='netbox_inventory/inc/buttons/audittrail_seen.html',
                    verbose_name='',  # No header like actions column
                    attrs={
                        'td': {
                            'class': 'w-1',
                        },
                    },
                ),
            ),
        ]
        table: NetBoxTable = self.table(
            data,
            user=request.user,
            extra_columns=extra_columns,
        )

        # Show newly created column and rearrange it to its static position. Users will
        # not be able to show/hide the column or change its position.
        table.columns.show('audit_trail_seen')
        table.exempt_columns += ('audit_trail_seen',)
        table.sequence.remove('audit_trail_seen')
        table.sequence.insert(1, 'audit_trail_seen')

        # Configure the table like a normal NetBoxTable. The code has to be copied here,
        # because calling super() would initialize the table and make it impossible to
        # change columns.
        if 'pk' in table.base_columns and bulk_actions:
            table.columns.show('pk')
        table.configure(request)
        return table

    def get_prefill_location_params(self) -> dict[str, int]:
        """
        Get object form parameters related to the location of a running audit flow.
        """
        # Create a map of possible location type models that can be used to pre-populate
        # forms. At least the original start object of the audit flow is used.
        # Additional data is added depending on its availability relative to the start
        # object.
        obj = self.start_object
        data = {obj._meta.model: obj.pk}

        if isinstance(obj, Rack):
            data[Location] = obj.location.pk
            data[Site] = obj.site.pk
        elif isinstance(obj, Location):
            data[Site] = obj.site.pk

        # Resolve the model add view for the associated model to access its form. Views
        # without a (standard) form attribute are skipped, as there's no clean way to
        # look up their form.
        view = resolve(reverse(get_viewname(self.child_model, 'add'))).func.view_class
        if not hasattr(view, 'form'):
            return {}

        # Map the available values to the actual form fields using the appropriate model
        # object types (depending on the actual model).
        result = {}
        for name, field in view.form().fields.items():
            if isinstance(field, ModelChoiceField):
                related_model = field.queryset.model
                if related_model in data:
                    result[name] = data[related_model]
        return result

    def get_prefill_variants(self) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        """
        Get static and variable parameters from the audit flow page's `object_filter` to
        pre-populate form fields when creating new objects.


        :returns: Tuple with a dict of static parameters and a list of dynamic parameter
            sets. Each list element contains a dictionary mapping the field name to its
            value.
        """
        model = self.page.page.object_type.model_class()
        filters = dict_to_filter_params(self.page.page.object_filter or {})
        if not filters:
            return {}, []

        static_filters = {}
        variant_groups = []
        related_fields = defaultdict(dict)
        for key, value in filters.items():
            if '__' in key:
                field, lookup = key.split('__', 1)

                # Choice filters pass through available choices as (static) variants.
                # Combinations with other lookups (e.g. 'startswith') are not supported.
                if lookup == 'in':
                    variant_groups.append([{field: v} for v in value])
                    continue

                # Other field lookups must be cumulated because multiple filters may
                # apply to the same field. These are handled in the next step.
                related_fields[field][lookup] = value
                continue

            # The only option left is static values: These will be passed as static
            # parameters for pre-population.
            static_filters[key] = value

        # Lookup filters can be used to filter an object field or to access related
        # objects. Options cannot be automatically generated for field values.
        # However, a choice set can be generated for related objects. If only a
        # single choice is available, it is treated as a static parameter.
        for field, field_filters in related_fields.items():
            related_model = model._meta.get_field(field).related_model
            if related_model:
                qs = related_model.objects.filter(**field_filters)
                if len(qs) == 1:
                    static_filters[field] = qs.first().pk
                elif len(qs) > 1:
                    variant_groups.append([{field: obj} for obj in qs])

        # Generate all possible variations of options. These variants define choices for
        # the user to select a specific variant to create, while static parameters can
        # be pre-populated for all forms.
        variants = []
        if variant_groups:
            variants = [
                {k: v for d in combo for k, v in d.items()}
                for combo in product(*variant_groups)
            ]

        return static_filters, variants

    def get_buttons(self) -> list[dict[str, str]]:
        """
        Get a list of buttons to create new objects directly from within the audit flow.
        """
        location_params = self.get_prefill_location_params()
        static_params, variants = self.get_prefill_variants()

        buttons = [
            {
                'name': ' '.join(map(str, variant.values())),
                'params': urlencode(
                    {
                        **{
                            # Use the object's pk if the variant refers to a model, as
                            # required by the form's ModelChoiceField.
                            k: (v.pk if isinstance(v, Model) else v)
                            for k, v in variant.items()
                        },
                        **static_params,
                        **location_params,
                    }
                ),
            }
            for variant in variants
        ]

        # Add a generic 'add' button with only static parameters pre-populated. It can
        # be used for more flexibility if the desired choice is not selected, and as a
        # fallback if there are no variant choices at all.
        buttons.append(
            {
                'name': self.child_model._meta.verbose_name,
                'params': urlencode({**static_params, **location_params}),
            }
        )

        return buttons

    def get_extra_context(self, request: HttpRequest, parent: models.AuditFlow) -> dict:
        return {
            'flow_pages': parent.assigned_pages.prefetch_related('page'),
            'start_object': self.start_object,
            'buttons': self.get_buttons(),
        }

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Automatically mark objects as seen based on filterset evaluation.
        """
        instance = self.get_object(**kwargs)
        child_objects = self.get_children(request, instance)

        if self.filterset:
            # Check the filterset of the current audit flow page. If it returns only a
            # single result, there is an exact object match and the object can be marked
            # as seen, i.e. an audit trail can be created.
            qs = self.filterset(request.POST, child_objects, request=request).qs
            if len(qs) == 1:
                obj = qs.first()
                models.AuditTrail.objects.create(object=obj)
                messages.success(
                    request,
                    _('Marked {object} as seen').format(object=obj),
                )

                return self.get(request, *args, **kwargs)

            # If the filterset returns a single object for the entire model queryset,
            # the object appears to exist but is not documented at the current audit
            # flow location. The user is redirected to its edit form to change its
            # location.
            #
            # NOTE: The object's location won't be changed automatically because
            #       dependent fields may require additional changes. However, available
            #       metadata will be pre-populated, just as when adding new items.
            qs = self.filterset(
                request.POST,
                self.child_model.objects.all(),
                request=request,
            ).qs
            if len(qs) == 1:
                obj = qs.first()
                messages.info(
                    request,
                    _(
                        '{object} does not match audit location. Please edit the '
                        'object accordingly.'
                    ).format(object=obj),
                )

                location_params = self.get_prefill_location_params()
                return redirect(
                    reverse(
                        get_viewname(self.child_model, 'edit'),
                        kwargs={'pk': obj.pk},
                    )
                    + '?'
                    + urlencode(
                        {
                            **location_params,
                            'return_url': request.get_full_path(),
                        }
                    )
                )

        # Fallback: If no matching object can be found, a warning is displayed. However,
        # the user is not redirected to the add view of the object, as there may be
        # multiple options to create it, or maybe it shouldn't be added to NetBox at
        # all.
        messages.error(request, _('No matching object found'))
        return self.get(request, *args, **kwargs)
