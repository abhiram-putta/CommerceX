# Database Migration Guide

Complete guide for setting up and managing database migrations with Alembic.

## Prerequisites

- PostgreSQL 14+ installed and running
- Database created
- Virtual environment activated
- Dependencies installed

## Initial Setup

### 1. Create Database

```bash
# Create the database
createdb smart_db

# Verify it was created
psql -l | grep smart_db
```

### 2. Configure Environment

Ensure your `.env` file has the correct `DATABASE_URL`:

```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/smart_db
```

## Creating Migrations

### Initial Migration

Create the initial migration with all models:

```bash
# Generate initial migration
alembic revision --autogenerate -m "Initial migration with all models"

# Review the generated migration in migrations/versions/
# Make any necessary adjustments

# Apply the migration
alembic upgrade head
```

### Models Included in Initial Migration

The initial migration will create these tables:

1. **users** - User accounts
2. **user_profiles** - Extended user information
3. **categories** - Product categories
4. **products** - Product catalog
5. **inventory** - Stock management
6. **stock_alerts** - Low stock alerts
7. **retailer_wholesaler_links** - B2B relationships
8. **carts** - Shopping cart items
9. **wishlists** - User wishlists
10. **orders** - Order records
11. **order_items** - Order line items
12. **order_tracking** - Order status history
13. **payments** - Payment transactions
14. **reviews** - Product reviews
15. **notifications** - User notifications
16. **user_interactions** - ML tracking data
17. **search_queries** - Search analytics

### Adding New Migrations

When you add or modify models:

```bash
# Create a new migration
alembic revision --autogenerate -m "Add new feature"

# Review the migration file
cat migrations/versions/<timestamp>_add_new_feature.py

# Apply the migration
alembic upgrade head
```

## Migration Commands

### Upgrade Database

```bash
# Upgrade to latest version
alembic upgrade head

# Upgrade to specific version
alembic upgrade <revision_id>

# Upgrade by one version
alembic upgrade +1
```

### Downgrade Database

```bash
# Downgrade by one version
alembic downgrade -1

# Downgrade to specific version
alembic downgrade <revision_id>

# Downgrade to base (drop all tables)
alembic downgrade base
```

### View History

```bash
# Show current version
alembic current

# Show migration history
alembic history

# Show verbose history
alembic history --verbose
```

### Check Status

```bash
# Show pending migrations
alembic heads

# Show all revisions
alembic branches
```

## Manual Migration Creation

If you need to create a migration manually:

```bash
# Create empty migration
alembic revision -m "Custom migration"
```

Then edit the generated file in `migrations/versions/`.

## Migration File Structure

Each migration file contains:

```python
"""Migration description

Revision ID: <unique_id>
Revises: <previous_revision>
Create Date: <timestamp>
"""

def upgrade():
    # SQL commands to upgrade
    pass

def downgrade():
    # SQL commands to downgrade
    pass
```

## Common Migration Tasks

### Add Column

```python
def upgrade():
    op.add_column('table_name',
        sa.Column('new_column', sa.String(255), nullable=True)
    )

def downgrade():
    op.drop_column('table_name', 'new_column')
```

### Add Index

```python
def upgrade():
    op.create_index(
        'idx_table_column',
        'table_name',
        ['column_name']
    )

def downgrade():
    op.drop_index('idx_table_column')
```

### Add Foreign Key

```python
def upgrade():
    op.create_foreign_key(
        'fk_table_ref',
        'source_table',
        'target_table',
        ['source_column'],
        ['target_column']
    )

def downgrade():
    op.drop_constraint('fk_table_ref', 'source_table')
```

## Recommended Indexes

After creating initial migration, consider adding these indexes for better performance:

```sql
-- Products
CREATE INDEX idx_products_category_active ON products(category_id, is_active);
CREATE INDEX idx_products_active_price ON products(is_active, base_price);

-- Orders
CREATE INDEX idx_orders_customer_status_date ON orders(customer_id, status, created_at DESC);

-- Cart
CREATE INDEX idx_cart_user_created ON cart(user_id, created_at DESC);

-- Reviews
CREATE INDEX idx_reviews_product_date ON reviews(product_id, created_at DESC);

-- Inventory
CREATE INDEX idx_inventory_product_seller ON inventory(product_id, seller_id);

-- Notifications
CREATE INDEX idx_notifications_user_read ON notifications(user_id, is_read, created_at DESC);
```

Add these in a separate migration:

```bash
alembic revision -m "Add performance indexes"
```

## Troubleshooting

### Error: "Target database is not up to date"

```bash
# Check current version
alembic current

# Upgrade to latest
alembic upgrade head
```

### Error: "Can't locate revision identified by"

```bash
# Stamp database to current code state
alembic stamp head
```

### Error: "Multiple head revisions are present"

```bash
# Merge the heads
alembic merge heads -m "Merge migrations"
```

### Start Fresh

If you need to reset everything:

```bash
# Drop all tables
alembic downgrade base

# Or drop and recreate database
dropdb smart_db
createdb smart_db

# Run migrations
alembic upgrade head
```

## Best Practices

### 1. Always Review Generated Migrations

Before applying, check the generated SQL:

```bash
alembic upgrade head --sql > migration.sql
cat migration.sql
```

### 2. Test Migrations

Test migrations on a copy of production data before applying to production.

### 3. Backup Before Major Migrations

```bash
pg_dump smart_db > backup_$(date +%Y%m%d).sql
```

### 4. Use Descriptive Messages

```bash
# Good
alembic revision -m "Add wishlist feature with user relationship"

# Bad
alembic revision -m "update"
```

### 5. Keep Migrations Small

Create separate migrations for different features rather than one large migration.

## Production Deployment

### Pre-Deployment Checklist

- [ ] Backup database
- [ ] Test migration on staging
- [ ] Review migration SQL
- [ ] Plan rollback strategy
- [ ] Notify team of downtime (if any)

### Apply Migration in Production

```bash
# 1. Backup
pg_dump production_db > backup_pre_migration.sql

# 2. Test on staging
alembic upgrade head --sql | psql staging_db

# 3. Apply to production
alembic upgrade head

# 4. Verify
alembic current
psql production_db -c "\dt"  # List tables
```

### Rollback if Needed

```bash
# Rollback last migration
alembic downgrade -1

# Restore from backup if necessary
psql production_db < backup_pre_migration.sql
```

## Migration Workflow

### Development

```mermaid
1. Modify models
   ↓
2. Generate migration
   ↓
3. Review migration
   ↓
4. Test locally
   ↓
5. Commit to git
```

### Staging

```mermaid
1. Pull latest code
   ↓
2. Run alembic upgrade head
   ↓
3. Test application
   ↓
4. Report issues or approve
```

### Production

```mermaid
1. Backup database
   ↓
2. Run migration in maintenance window
   ↓
3. Verify success
   ↓
4. Monitor application
```

## Quick Reference

```bash
# Setup
alembic init migrations              # Initialize (already done)
createdb smart_db                    # Create database

# Create migrations
alembic revision --autogenerate -m "message"  # Auto-generate
alembic revision -m "message"                  # Manual

# Apply migrations
alembic upgrade head                 # Upgrade to latest
alembic upgrade +1                   # Upgrade one version
alembic downgrade -1                 # Downgrade one version
alembic downgrade base               # Downgrade all

# View status
alembic current                      # Current version
alembic history                      # Migration history
alembic heads                        # Pending migrations

# Utilities
alembic stamp head                   # Mark as current without running
alembic merge heads -m "merge"       # Merge multiple heads
```

## Support

For issues with migrations:
1. Check this guide
2. Review Alembic documentation
3. Check database logs
4. Verify model definitions

---

**Ready to create your first migration!**

```bash
alembic revision --autogenerate -m "Initial migration with all models"
alembic upgrade head
```
