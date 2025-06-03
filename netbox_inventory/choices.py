from utilities.choices import ChoiceSet

#
# Assets
#


class AssetStatusChoices(ChoiceSet):
    key = 'Asset.status'

    CHOICES = [
        ('stored', 'Stored', 'green'),
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


class PurchaseStatusChoices(ChoiceSet):
    key = 'Purchase.status'

    CHOICES = [
        ('open', 'Open', 'cyan'),
        ('partial', 'Partial', 'blue'),
        ('closed', 'Closed', 'green'),
    ]


#
# Contracts
#


class ContractStatusChoices(ChoiceSet):
    key = 'Contract.status'

    CHOICES = [
        ('draft', 'Draft', 'gray'),
        ('active', 'Active', 'green'),
        ('expired', 'Expired', 'red'),
        ('cancelled', 'Cancelled', 'orange'),
        ('renewed', 'Renewed', 'blue'),
    ]


class ContractTypeChoices(ChoiceSet):
    key = 'Contract.contract_type'

    CHOICES = [
        ('warranty', 'Warranty', 'blue'),
        ('support', 'Support', 'green'),
        ('maintenance', 'Maintenance', 'orange'),
        ('service', 'Service', 'purple'),
        ('lease', 'Lease', 'cyan'),
        ('other', 'Other', 'gray'),
    ]
