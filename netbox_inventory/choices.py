from utilities.choices import ChoiceSet

#
# Assets
#


class AssetStatusChoices(ChoiceSet):
    key = 'Asset.status'

    CHOICES = [
        ('planned', 'Planned', 'orange'),
        ('ordered', 'Ordered', 'cyan'),
        ('stored', 'Stored', 'green'),
        ('transit', 'In Transit', 'purple'),
        ('used', 'Used', 'blue'),
        ('retired', 'Retired', 'gray'),
    ]


class HardwareKindChoices(ChoiceSet):
    CHOICES = [
        ('device', 'Device'),
        ('module', 'Module'),
        ('inventoryitem', 'Inventory Item'),
        ('rack', 'Rack'),
    ]


#
# Deliveries
#


class BOMStatusChoices(ChoiceSet):
    key = 'BOM.status'

    CHOICES = [
        ('planned', 'Planned', 'orange'),
        ('quoted', 'Quoted', 'cyan'),
        ('closed', 'Closed', 'green'),
    ]


class PurchaseStatusChoices(ChoiceSet):
    key = 'Purchase.status'

    CHOICES = [
        ('open', 'Open', 'cyan'),
        ('partial', 'Partial', 'blue'),
        ('closed', 'Closed', 'green'),
    ]


#
# Transit
#


class TransferStatusChoices(ChoiceSet):
    key = 'Transfer.status'

    CHOICES = [
        ('created', 'Created', 'orange'),
        ('pickedup', 'Picked Up', 'cyan'),
        ('delivered', 'Delivered', 'green'),
    ]