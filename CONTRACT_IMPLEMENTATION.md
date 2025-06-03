# Contract Model Implementation for NetBox Inventory Plugin

## Overview
This implementation adds a Contract model to the NetBox Inventory plugin that can be associated with existing Asset objects. The Contract model allows tracking of warranty, support, maintenance, and other contractual agreements.

## Changes Made

### 1. Models
- **Created `netbox_inventory/models/contracts.py`**:
  - `Contract` model with fields for contract management
  - Relationship to `Supplier` model
  - Contract types: warranty, support, maintenance, service, lease, other
  - Contract statuses: draft, active, expired, cancelled, renewed
  - Date tracking: start_date, end_date, renewal_date
  - Financial tracking: cost, currency
  - Helper properties: `is_active`, `days_until_expiry`, `is_expired`, `needs_renewal`

- **Updated `netbox_inventory/models/assets.py`**:
  - Added `contract` ForeignKey field to Asset model
  - Added contract to clone_fields

- **Updated `netbox_inventory/models/__init__.py`**:
  - Added import for contracts module

### 2. Choices
- **Updated `netbox_inventory/choices.py`**:
  - Added `ContractStatusChoices`
  - Added `ContractTypeChoices`

### 3. Database Migration
- **Created `netbox_inventory/migrations/0011_add_contract_model.py`**:
  - Creates Contract table
  - Adds contract field to Asset table
  - Sets up proper relationships and constraints

### 4. Forms
- **Updated `netbox_inventory/forms/models.py`**:
  - Added `ContractForm` with proper fieldsets and widgets
  - Updated `AssetForm` to include contract field
  - Added contract to Purchase fieldset in AssetForm

### 5. Navigation
- **Updated `netbox_inventory/navigation.py`**:
  - Added contract navigation buttons
  - Added Contracts menu item to deliveries section

## Contract Model Fields

| Field | Type | Description |
|-------|------|-------------|
| name | CharField | Contract name or identifier |
| contract_id | CharField | External contract identifier (optional) |
| supplier | ForeignKey | Supplier providing the contract |
| contract_type | CharField | Type of contract (warranty, support, etc.) |
| status | CharField | Current status of the contract |
| start_date | DateField | Contract effective date |
| end_date | DateField | Contract expiration date |
| renewal_date | DateField | Contract renewal date (optional) |
| cost | DecimalField | Total cost of the contract (optional) |
| currency | CharField | Currency code (default: USD) |
| description | CharField | Brief description |
| comments | TextField | Additional notes |

## Next Steps Required

### 1. Views and URLs
- Create views for Contract CRUD operations
- Add URL patterns for contract views
- Update main urls.py to include contract URLs

### 2. Templates
- Create HTML templates for contract list, detail, add, edit views
- Add contract information to asset detail templates

### 3. API Integration
- Add Contract serializers
- Update API views and URLs
- Add contract field to Asset API serializer

### 4. Tables and Filters
- Add Contract to tables.py
- Add contract filters to filtersets.py
- Update search functionality

### 5. Testing
- Create unit tests for Contract model
- Test Asset-Contract relationship
- Test form validation

## Installation Instructions

1. **Commit and push changes to your repository**:
   ```bash
   git add .
   git commit -m "Add Contract model and Asset-Contract relationship"
   git push origin main
   ```

2. **Install/update the plugin on your NetBox server**:
   ```bash
   pip install git+https://github.com/yourusername/netbox-inventory.git
   ```

3. **Apply database migrations**:
   ```bash
   python manage.py migrate
   ```

4. **Restart NetBox service**:
   ```bash
   sudo systemctl restart netbox
   ```

## Usage

Once fully implemented, users will be able to:
- Create and manage contracts with suppliers
- Associate contracts with assets
- Track contract dates and renewal requirements
- Monitor contract costs and financial information
- Filter and search assets by contract information

## Contract-Asset Relationship

- **One-to-Many**: One contract can be associated with multiple assets
- **Optional**: Assets can exist without contracts
- **Protected**: Contracts cannot be deleted if they have associated assets
- **Accessible**: Assets can access contract information via `asset.contract`
- **Reverse Accessible**: Contracts can access associated assets via `contract.assets.all()`