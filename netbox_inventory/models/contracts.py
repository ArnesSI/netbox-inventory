from django.db import models
from django.urls import reverse
from django.db.models.signals import pre_save
from django.dispatch import receiver

from netbox.models import NetBoxModel

from ..choices import ContractStatusChoices, ContractTypeChoices


class Contract(NetBoxModel):
    """
    Contract represents a service or support contract that can be associated with Assets.
    This allows tracking of warranty, support, maintenance, and other contractual agreements.
    """

    name = models.CharField(
        max_length=100,
        help_text='Contract name or identifier',
    )
    contract_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text='External contract identifier or number',
        verbose_name='Contract ID',
    )
    supplier = models.ForeignKey(
        to='netbox_inventory.Supplier',
        on_delete=models.PROTECT,
        related_name='contracts',
        help_text='Supplier providing the contract',
    )
    contract_type = models.CharField(
        max_length=30,
        choices=ContractTypeChoices,
        help_text='Type of contract',
        verbose_name='Contract Type',
    )
    status = models.CharField(
        max_length=30,
        choices=ContractStatusChoices,
        help_text='Current status of the contract',
    )
    start_date = models.DateField(
        help_text='Date when the contract becomes effective',
        verbose_name='Start Date',
    )
    end_date = models.DateField(
        help_text='Date when the contract expires',
        verbose_name='End Date',
    )
    renewal_date = models.DateField(
        blank=True,
        null=True,
        help_text='Date when the contract is up for renewal',
        verbose_name='Renewal Date',
    )
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='Total cost of the contract',
    )
    currency = models.CharField(
        max_length=3,
        blank=True,
        help_text='Currency code (e.g., USD, EUR, GBP)',
    )
    # Contact field that would have been provided by ContactsMixin
    contact = models.ForeignKey(
        to='tenancy.Contact',
        on_delete=models.PROTECT,
        related_name='contracts',
        blank=True,
        null=True,
        help_text='Primary contact for this contract',
    )
    description = models.CharField(
        max_length=200,
        blank=True,
        help_text='Brief description of the contract',
    )
    comments = models.TextField(
        blank=True,
        help_text='Additional comments or notes',
    )

    clone_fields = [
        'supplier', 'contract_type', 'status', 'cost', 'currency', 
        'description', 'contact'
    ]

    class Meta:
        ordering = ['name']
        unique_together = [['supplier', 'contract_id']]

    def __str__(self):
        if self.contract_id:
            return f'{self.name} ({self.contract_id})'
        return self.name

    def get_absolute_url(self):
        return reverse('plugins:netbox_inventory:contract', args=[self.pk])

    def get_status_color(self):
        return ContractStatusChoices.colors.get(self.status)

    @property
    def is_active(self):
        """Check if the contract is currently active based on dates."""
        from datetime import date
        today = date.today()
        return self.start_date <= today <= self.end_date

    @property
    def days_until_expiry(self):
        """Calculate days until contract expires."""
        from datetime import date
        today = date.today()
        if self.end_date > today:
            return (self.end_date - today).days
        return 0

    @property
    def is_expired(self):
        """Check if the contract has expired."""
        from datetime import date
        return self.end_date < date.today()

    @property
    def needs_renewal(self):
        """Check if the contract needs renewal based on renewal date."""
        if not self.renewal_date:
            return False
        from datetime import date
        return date.today() >= self.renewal_date

    @property
    def remaining_time_display(self):
        """Get a user-friendly display of remaining contract time."""
        if self.is_expired:
            from django.utils.timesince import timesince
            return f"Expired {timesince(self.end_date)} ago"
        elif self.days_until_expiry <= 0:
            return "Expires today"
        elif self.days_until_expiry == 1:
            return "1 day remaining"
        else:
            return f"{self.days_until_expiry} days remaining"

    @property
    def remaining_time_class(self):
        """Get the CSS class for the remaining time badge."""
        if self.is_expired or self.days_until_expiry <= 0:
            return "bg-danger"
        elif self.days_until_expiry <= 7:
            return "bg-danger"
        elif self.days_until_expiry <= 30:
            return "bg-warning"
        elif self.days_until_expiry <= 90:
            return "bg-info"
        else:
            return "bg-success"

    @property
    def remaining_time_icon(self):
        """Get the icon for the remaining time badge."""
        if self.is_expired or self.days_until_expiry <= 0:
            return "mdi-alert-circle"
        elif self.days_until_expiry <= 30:
            return "mdi-alert"
        elif self.days_until_expiry <= 90:
            return "mdi-information"
        else:
            return "mdi-check-circle"

    @property
    def contract_duration_days(self):
        """Get the total duration of the contract in days."""
        if not self.start_date or not self.end_date:
            return None
        return (self.end_date - self.start_date).days

    @property
    def days_elapsed(self):
        """Get the number of days elapsed since contract start."""
        if not self.start_date:
            return None
        from datetime import date
        today = date.today()
        if today < self.start_date:
            return 0  # Contract hasn't started yet
        return (today - self.start_date).days

    @property
    def progress_percentage(self):
        """Get the contract progress as a percentage (0-100)."""
        if not self.contract_duration_days or self.contract_duration_days <= 0:
            return 0
        if self.is_expired:
            return 100
        if self.days_elapsed is None or self.days_elapsed < 0:
            return 0
        return min(100, (self.days_elapsed / self.contract_duration_days) * 100)

    def update_status_based_on_dates(self):
        """
        Update contract status based on current date and contract dates.
        Returns True if status was changed, False otherwise.
        """
        from datetime import date
        today = date.today()
        original_status = self.status
        
        # Only auto-update if current status allows it
        # Don't override manually set statuses like 'cancelled' or 'renewed'
        if self.status in ['draft', 'active', 'expired']:
            if self.end_date < today:
                # Contract has expired
                self.status = 'expired'
            elif self.start_date <= today <= self.end_date:
                # Contract is currently active
                if self.status != 'active':
                    self.status = 'active'
            elif self.start_date > today:
                # Contract hasn't started yet
                if self.status not in ['draft']:
                    self.status = 'draft'
        
        return self.status != original_status


@receiver(pre_save, sender=Contract)
def auto_update_contract_status(sender, instance, **kwargs):
    """
    Automatically update contract status based on dates when saving.
    """
    instance.update_status_based_on_dates()