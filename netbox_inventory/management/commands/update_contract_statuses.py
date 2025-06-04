from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date

from netbox_inventory.models import Contract


class Command(BaseCommand):
    help = 'Update contract statuses based on current date and contract expiration dates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output for each contract processed',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        verbose = options['verbose']
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Starting contract status update {"(DRY RUN)" if dry_run else ""}'
            )
        )
        
        # Get all contracts that might need status updates
        contracts = Contract.objects.filter(
            status__in=['draft', 'active', 'expired']
        )
        
        updated_count = 0
        total_count = contracts.count()
        
        for contract in contracts:
            original_status = contract.status
            status_changed = contract.update_status_based_on_dates()
            
            if status_changed:
                if verbose or dry_run:
                    self.stdout.write(
                        f'Contract "{contract.name}" ({contract.pk}): '
                        f'{original_status} → {contract.status} '
                        f'(expires: {contract.end_date})'
                    )
                
                if not dry_run:
                    contract.save()
                
                updated_count += 1
            elif verbose:
                self.stdout.write(
                    f'Contract "{contract.name}" ({contract.pk}): '
                    f'No change needed (status: {contract.status}, expires: {contract.end_date})'
                )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: Would update {updated_count} of {total_count} contracts'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated {updated_count} of {total_count} contracts'
                )
            )
            
        # Show summary of contracts by status
        if verbose or updated_count > 0:
            self.stdout.write('\nContract status summary:')
            for status_choice in Contract._meta.get_field('status').choices:
                status_value = status_choice[0]
                status_label = status_choice[1]
                count = Contract.objects.filter(status=status_value).count()
                self.stdout.write(f'  {status_label}: {count}') 