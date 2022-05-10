from utilities.choices import ChoiceSet

class InventoryStatusChoices(ChoiceSet):
    key = 'Inventory.status'

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
