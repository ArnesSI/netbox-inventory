from utilities.choices import ChoiceSet

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
    ]

class ConsumableQuantityStatusChoices(ChoiceSet):
    key = 'Consumable.quantity_status'

    CHOICES = [
        ('In-Stock', 'In-Stock', 'green'),
        ('Low-Stock', 'Low-Stock', 'red')
    ]