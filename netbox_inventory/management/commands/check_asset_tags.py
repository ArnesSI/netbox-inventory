from typing import Any
from django.db.models import Count
from django.core.management.base import BaseCommand, CommandError, CommandParser

from netbox_inventory.models import Asset


class Command(BaseCommand):
    help = "Check netbox-inventory assets if asset tags are unique"

    def handle(self, *args: Any, **options: Any) -> str | None:
        dup_tags = Asset.objects.filter(owner__isnull=True, asset_tag__isnull=False).values('asset_tag').annotate(count=Count('id')).order_by('asset_tag').filter(count__gt=1)
        dup_tags = list(dup_tags.values_list('asset_tag', flat=True))
        if not dup_tags:
            print('No duplicate asset tags found. You\'re good to go.')
            return

        print(f'Duplicate asset tags with no owner: {dup_tags}')
        print('You\'ll want to fix this before upgrading to next major version of netbox-inventory. See https://github.com/ArnesSI/netbox-inventory/releases for more info')
        print('List of problematic assets follows.')
        print()
        assets = Asset.objects.filter(owner__isnull=True, asset_tag__isnull=False).filter(asset_tag__in=dup_tags).order_by('asset_tag', 'id')
        print('id, asset, asset_tag')
        for asset in assets:
            print(f'{asset.id}, "{asset}", {asset.asset_tag}')
