from .schema import (
    AssetQuery,
    SupplierQuery,
    PurchaseQuery,
    DeliveryQuery,
    InventoryItemTypeQuery,
    InventoryItemGroupQuery
)

schema = [
    AssetQuery,
    # SupplierQuery,
    # PurchaseQuery,
    # DeliveryQuery,
    # InventoryItemTypeQuery,
    # InventoryItemGroupQuery # Commented out to due to circular dependency
]