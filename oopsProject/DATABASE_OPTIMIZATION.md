# Database Optimization Guide

This document outlines database optimization strategies and index recommendations for the sMart e-commerce backend.

## Current Index Status

### Existing Indexes (from models)

**Products Table:**
- `name` - B-tree index
- `slug` - Unique B-tree index
- `category_id` - B-tree index (FK)
- `brand` - B-tree index
- `is_local_product` - B-tree index
- `is_active` - B-tree index

**Users Table:**
- `email` - Unique B-tree index
- `username` - Unique B-tree index

**Orders Table:**
- `customer_id` - B-tree index (FK)
- `order_number` - Unique B-tree index
- `status` - B-tree index

## Recommended Additional Indexes

### 1. Composite Indexes for Common Queries

```sql
-- Products: Filter by category and active status (common in listings)
CREATE INDEX idx_products_category_active ON products(category_id, is_active);

-- Products: Filter by active and featured (home page queries)
CREATE INDEX idx_products_active_featured ON products(is_active, is_featured);

-- Products: Price range queries with active filter
CREATE INDEX idx_products_active_price ON products(is_active, base_price);

-- Orders: User's orders by status and date
CREATE INDEX idx_orders_customer_status_date ON orders(customer_id, status, created_at DESC);

-- Cart: Active cart items for user
CREATE INDEX idx_cart_user_created ON cart(user_id, created_at DESC);

-- Reviews: Product reviews sorted by date
CREATE INDEX idx_reviews_product_date ON reviews(product_id, created_at DESC);

-- Inventory: Product stock lookup by seller
CREATE INDEX idx_inventory_product_seller ON inventory(product_id, seller_id);

-- Notifications: Unread notifications for user
CREATE INDEX idx_notifications_user_read ON notifications(user_id, is_read, created_at DESC);
```

### 2. Full-Text Search Indexes

```sql
-- Products: Full-text search on name and description
CREATE INDEX idx_products_search ON products
USING GIN(to_tsvector('english', name || ' ' || COALESCE(description, '')));

-- Search with weights (name has higher weight)
CREATE INDEX idx_products_weighted_search ON products
USING GIN(
  setweight(to_tsvector('english', name), 'A') ||
  setweight(to_tsvector('english', COALESCE(description, '')), 'B')
);
```

### 3. Partial Indexes for Specific Queries

```sql
-- Active products only (most queries filter by active)
CREATE INDEX idx_products_active_only ON products(created_at DESC)
WHERE is_active = true;

-- Featured products only
CREATE INDEX idx_products_featured_only ON products(created_at DESC)
WHERE is_featured = true;

-- Pending orders only (frequent admin queries)
CREATE INDEX idx_orders_pending ON orders(created_at DESC)
WHERE status = 'PENDING';

-- Low stock alerts
CREATE INDEX idx_inventory_low_stock ON inventory(product_id, seller_id)
WHERE stock_quantity < 10;
```

### 4. JSONB Indexes

```sql
-- Product specifications search
CREATE INDEX idx_products_specifications ON products USING GIN(specifications);

-- Product images (if querying specific image properties)
CREATE INDEX idx_products_images ON products USING GIN(images);
```

## Query Optimization Strategies

### 1. Use SELECT Specific Columns

**Bad:**
```python
products = await session.execute(select(Product))
```

**Good:**
```python
products = await session.execute(
    select(Product.id, Product.name, Product.base_price)
)
```

### 2. Eager Loading for Relationships

**Bad (N+1 queries):**
```python
products = await session.execute(select(Product))
for product in products:
    category = product.category  # Separate query for each
```

**Good (Single query with JOIN):**
```python
products = await session.execute(
    select(Product).options(selectinload(Product.category))
)
```

### 3. Pagination with Limit/Offset

Always use pagination for list queries:

```python
query = select(Product).where(Product.is_active == True)
query = query.order_by(Product.created_at.desc())
query = query.offset(skip).limit(limit)
```

### 4. Use Bulk Operations

**Bad:**
```python
for item in items:
    await session.execute(insert(Cart).values(item))
    await session.commit()
```

**Good:**
```python
await session.execute(insert(Cart), items)
await session.commit()
```

### 5. Count Optimization

**Bad:**
```python
products = await session.execute(select(Product))
count = len(products.all())
```

**Good:**
```python
from sqlalchemy import func
count = await session.scalar(select(func.count(Product.id)))
```

## Repository Pattern Optimizations

### Implemented Optimizations

1. **Base Repository** (`app/core/base_classes.py`)
   - Generic CRUD operations
   - Pagination support
   - Bulk operations

2. **Specific Repositories**
   - Use `selectinload` for relationships
   - Filter on indexed columns
   - Order by indexed columns

### Example: Optimized Product Query

```python
async def get_active_products(
    self,
    category_id: Optional[UUID] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    skip: int = 0,
    limit: int = 20
) -> List[Product]:
    """Get active products with filters (uses indexes)."""
    query = select(Product).where(Product.is_active == True)

    if category_id:
        # Uses idx_products_category_active
        query = query.where(Product.category_id == category_id)

    if min_price is not None:
        # Uses idx_products_active_price
        query = query.where(Product.base_price >= min_price)

    if max_price is not None:
        query = query.where(Product.base_price <= max_price)

    # Order by indexed column
    query = query.order_by(Product.created_at.desc())

    # Pagination
    query = query.offset(skip).limit(limit)

    # Eager load category
    query = query.options(selectinload(Product.category))

    result = await self.db.execute(query)
    return list(result.scalars().all())
```

## Caching Strategy

### 1. Redis Caching for Hot Data

Cache frequently accessed, rarely changed data:

```python
# Product details (TTL: 1 hour)
CACHE_KEY = f"product:{product_id}"
TTL = 3600

# Category list (TTL: 24 hours)
CACHE_KEY = "categories:all"
TTL = 86400

# User cart count (TTL: 5 minutes)
CACHE_KEY = f"cart:count:{user_id}"
TTL = 300
```

### 2. Cache Invalidation

Invalidate cache when data changes:

```python
async def update_product(self, product_id: UUID, data: dict):
    # Update in database
    product = await self.update(product_id, data)

    # Invalidate cache
    await redis_client.delete(f"product:{product_id}")

    return product
```

## Connection Pool Configuration

**Current Settings** (`app/config/settings.py`):
```python
DATABASE_POOL_SIZE: int = 20
DATABASE_MAX_OVERFLOW: int = 10
```

**Recommendations:**
- Development: pool_size=5, max_overflow=5
- Production: pool_size=20, max_overflow=20
- Monitor connections: `SELECT count(*) FROM pg_stat_activity;`

## Database Maintenance

### 1. Regular VACUUM

```sql
-- Analyze and update statistics
ANALYZE products;

-- Full vacuum (locks table)
VACUUM FULL products;

-- Vacuum with analyze
VACUUM ANALYZE products;
```

### 2. Monitor Query Performance

```sql
-- Enable slow query logging
SET log_min_duration_statement = 1000; -- Log queries > 1 second

-- Check slow queries
SELECT query, mean_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

### 3. Index Usage Statistics

```sql
-- Check if indexes are being used
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan ASC;
```

## Migration Script

To apply these optimizations, create a new Alembic migration:

```bash
# Create new migration
alembic revision -m "add_performance_indexes"

# Edit the generated file in migrations/versions/
# Add the CREATE INDEX statements from above

# Apply migration
alembic upgrade head
```

## Performance Monitoring

### Key Metrics to Monitor

1. **Query Performance**
   - Average query time
   - Slow query count (> 1s)
   - Most frequent queries

2. **Connection Pool**
   - Active connections
   - Idle connections
   - Connection wait time

3. **Cache Hit Rate**
   - Redis cache hit ratio
   - Database query cache hit ratio

4. **Database Size**
   - Table sizes
   - Index sizes
   - Growth rate

### Tools

- **pgAdmin**: Database management and monitoring
- **pg_stat_statements**: Query statistics
- **Redis CLI**: Cache monitoring (`INFO stats`)
- **FastAPI Middleware**: Request timing logs

## Implementation Checklist

- [ ] Create Alembic migration for composite indexes
- [ ] Add full-text search indexes
- [ ] Implement caching layer in repositories
- [ ] Add query performance logging
- [ ] Set up database monitoring
- [ ] Configure connection pooling for production
- [ ] Schedule regular VACUUM jobs
- [ ] Review and optimize slow queries
- [ ] Add database query metrics to analytics

## Expected Performance Improvements

With these optimizations:
- **Product listing queries**: 50-70% faster
- **Search queries**: 80-90% faster (with full-text search)
- **User cart/orders**: 40-60% faster
- **Overall API response time**: 30-50% reduction
- **Database load**: 40-60% reduction
- **Cache hit rate**: 70-90% for hot data
