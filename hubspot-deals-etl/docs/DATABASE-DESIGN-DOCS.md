# 🗄️ HubSpot Deals Database Schema Design

This document provides the database schema design for storing HubSpot deals data extracted from HubSpot CRM API v3, along with scan job management.

---

## 📋 Overview

The database schema consists of two main components:

1. **ScanJob** - Core scan job management and tracking
2. **Deals** - Storage for extracted deal data with ETL metadata

### **Design Principles**

- **Multi-tenant support**: All tables include `organization_id` for tenant isolation
- **ETL metadata**: Every deal record includes extraction metadata (`_extracted_at`, `_scan_id`, `_tenant_id`)
- **Performance**: Indexes optimized for common queries (tenant, dates, stages)
- **Flexibility**: Support for custom properties via JSON columns
- **Data integrity**: Foreign key constraints and data type validation

---

## 🏗️ Table Schemas

### 1. ScanJob Table

**Purpose**: Core scan job management and status tracking

| **Column Name**         | **Type**    | **Constraints**           | **Description**                          |
|-------------------------|-------------|---------------------------|------------------------------------------|
| `id`                    | String      | PRIMARY KEY               | Unique internal identifier               |
| `scan_id`               | String      | UNIQUE, NOT NULL, INDEX   | External scan identifier                 |
| `status`                | String      | NOT NULL, INDEX           | pending, running, completed, failed, cancelled |
| `scan_type`             | String      | NOT NULL                  | Type of scan (user, project, calendar, etc.) |
| `config`                | JSON        | NOT NULL                  | Scan configuration and parameters        |
| `organization_id`       | String      | NULLABLE                  | Organization/tenant identifier           |
| `error_message`         | Text        | NULLABLE                  | Error details if scan failed            |
| `started_at`            | DateTime    | NULLABLE                  | When scan execution started             |
| `completed_at`          | DateTime    | NULLABLE                  | When scan finished                      |
| `total_items`           | Integer     | DEFAULT 0                 | Total items to process                  |
| `processed_items`       | Integer     | DEFAULT 0                 | Items successfully processed            |
| `failed_items`          | Integer     | DEFAULT 0                 | Items that failed processing            |
| `success_rate`          | String      | NULLABLE                  | Calculated success percentage           |
| `batch_size`            | Integer     | DEFAULT 50                | Processing batch size                   |
| `created_at`            | DateTime    | NOT NULL                  | Record creation timestamp               |
| `updated_at`            | DateTime    | NOT NULL                  | Record last update timestamp            |

**Indexes:**
```sql
-- Performance indexes
CREATE INDEX idx_scan_status_created ON scan_jobs(status, created_at);
CREATE INDEX idx_scan_id_status ON scan_jobs(scan_id, status);
CREATE INDEX idx_scan_type_status ON scan_jobs(scan_type, status);
CREATE INDEX idx_scan_org_status ON scan_jobs(organization_id, status);
```

---

### 2. Deals Table

**Purpose**: Store extracted HubSpot deal data with ETL metadata

| **Column Name**         | **Type**    | **Constraints**           | **Description**                          |
|-------------------------|-------------|---------------------------|------------------------------------------|
| `id`                    | VARCHAR(50) | PRIMARY KEY               | Unique deal identifier (HubSpot deal ID) |
| `scan_job_id`           | VARCHAR(50) | FOREIGN KEY, NOT NULL     | Reference to scan_jobs.id                |
| `_scan_id`              | VARCHAR(255)| NOT NULL, INDEX           | Scan identifier for this extraction      |
| `_tenant_id`            | VARCHAR(255)| NOT NULL, INDEX           | Organization/tenant identifier           |
| `_extracted_at`         | TIMESTAMP   | NOT NULL, INDEX           | When this record was extracted           |
| `dealname`              | VARCHAR(500)| NULLABLE                  | Deal name                                |
| `amount`                | NUMERIC(15,2)| NULLABLE                 | Deal amount                              |
| `dealstage`             | VARCHAR(100)| NULLABLE, INDEX           | Deal stage ID                            |
| `pipeline`              | VARCHAR(100)| NULLABLE, INDEX           | Pipeline ID                              |
| `createdate`            | TIMESTAMP   | NULLABLE, INDEX           | Creation date from HubSpot               |
| `closedate`             | TIMESTAMP   | NULLABLE, INDEX           | Close date (if deal is closed)           |
| `dealtype`              | VARCHAR(50) | NULLABLE                  | Deal type (newbusiness, existingbusiness)|
| `hubspot_owner_id`      | VARCHAR(50) | NULLABLE                  | HubSpot owner user ID                    |
| `description`           | TEXT        | NULLABLE                  | Deal description                         |
| `deal_currency_code`    | VARCHAR(10) | NULLABLE                  | Currency code (e.g., "USD")              |
| `hs_next_step`          | VARCHAR(500)| NULLABLE                  | Next step                                |
| `hs_priority`           | VARCHAR(50) | NULLABLE                  | Deal priority                            |
| `archived`              | BOOLEAN     | DEFAULT FALSE, INDEX      | Whether deal is archived                 |
| `properties`            | JSONB       | NULLABLE                  | All deal properties (custom fields)      |
| `hubspot_created_at`    | TIMESTAMP   | NULLABLE                  | Original creation timestamp from HubSpot |
| `hubspot_updated_at`    | TIMESTAMP   | NULLABLE                  | Last update timestamp from HubSpot       |
| `created_at`            | TIMESTAMP   | NOT NULL DEFAULT NOW()    | Record creation timestamp                |
| `updated_at`            | TIMESTAMP   | NOT NULL DEFAULT NOW()    | Record last update timestamp             |

**PostgreSQL Data Type Mapping:**

HubSpot deals properties are mapped to PostgreSQL types as follows:

| HubSpot Property | HubSpot Type | PostgreSQL Type | Notes |
|-----------------|--------------|-----------------|-------|
| `dealname` | String | `VARCHAR(500)` | Deal name |
| `amount` | Number | `NUMERIC(15,2)` | Deal amount with 2 decimal places |
| `dealstage` | Enum/String | `VARCHAR(100)` | Deal stage ID |
| `pipeline` | Enum/String | `VARCHAR(100)` | Pipeline ID |
| `createdate` | DateTime | `TIMESTAMP` | Creation date (UTC) |
| `closedate` | DateTime | `TIMESTAMP` | Close date (UTC, nullable) |
| `dealtype` | Enum | `VARCHAR(50)` | Deal type enum value |
| `description` | String | `TEXT` | Deal description |
| `archived` | Boolean | `BOOLEAN` | Archived flag |
| Custom properties | Various | `JSONB` | All custom properties stored in JSONB column |

**CREATE TABLE Statement:**
```sql
CREATE TABLE deals (
    id VARCHAR(50) PRIMARY KEY,
    scan_job_id VARCHAR(50) NOT NULL REFERENCES scan_jobs(id) ON DELETE CASCADE,
    _scan_id VARCHAR(255) NOT NULL,
    _tenant_id VARCHAR(255) NOT NULL,
    _extracted_at TIMESTAMP NOT NULL,
    dealname VARCHAR(500),
    amount NUMERIC(15,2),
    dealstage VARCHAR(100),
    pipeline VARCHAR(100),
    createdate TIMESTAMP,
    closedate TIMESTAMP,
    dealtype VARCHAR(50),
    hubspot_owner_id VARCHAR(50),
    description TEXT,
    deal_currency_code VARCHAR(10),
    hs_next_step VARCHAR(500),
    hs_priority VARCHAR(50),
    archived BOOLEAN DEFAULT FALSE,
    properties JSONB,
    hubspot_created_at TIMESTAMP,
    hubspot_updated_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Performance indexes for common queries
CREATE INDEX idx_deals_scan_job_id ON deals(scan_job_id);
CREATE INDEX idx_deals_scan_id ON deals(_scan_id);
CREATE INDEX idx_deals_tenant_id ON deals(_tenant_id);
CREATE INDEX idx_deals_extracted_at ON deals(_extracted_at);
CREATE INDEX idx_deals_tenant_scan ON deals(_tenant_id, _scan_id);
CREATE INDEX idx_deals_stage ON deals(dealstage) WHERE dealstage IS NOT NULL;
CREATE INDEX idx_deals_pipeline ON deals(pipeline) WHERE pipeline IS NOT NULL;
CREATE INDEX idx_deals_create_date ON deals(createdate) WHERE createdate IS NOT NULL;
CREATE INDEX idx_deals_close_date ON deals(closedate) WHERE closedate IS NOT NULL;
CREATE INDEX idx_deals_archived ON deals(archived) WHERE archived = FALSE;
CREATE INDEX idx_deals_tenant_date ON deals(_tenant_id, createdate);

-- Composite indexes for common query patterns
CREATE INDEX idx_deals_tenant_stage ON deals(_tenant_id, dealstage) WHERE dealstage IS NOT NULL;
CREATE INDEX idx_deals_tenant_pipeline ON deals(_tenant_id, pipeline) WHERE pipeline IS NOT NULL;
CREATE INDEX idx_deals_stage_date ON deals(dealstage, closedate) WHERE closedate IS NOT NULL;

-- JSONB index for properties field (for custom property queries)
CREATE INDEX idx_deals_properties_gin ON deals USING GIN (properties);
```

**Index Design Rationale:**

1. **Tenant Isolation**: `idx_deals_tenant_id` ensures fast filtering by organization
2. **Scan Tracking**: `idx_deals_scan_id` and `idx_deals_tenant_scan` for scan-based queries
3. **Date Filtering**: `idx_deals_create_date`, `idx_deals_close_date` for date range queries
4. **Stage/Pipeline Analysis**: `idx_deals_stage`, `idx_deals_pipeline` for deal stage queries
5. **Composite Indexes**: `idx_deals_tenant_stage`, `idx_deals_tenant_pipeline` for multi-tenant filtered queries
6. **JSONB Index**: `idx_deals_properties_gin` enables efficient queries on custom properties

---

---

## 🔗 Relationships

### Primary Relationships
```sql
-- ScanJob to Deals (One-to-Many)
scan_jobs.id ← deals.scan_job_id

-- Tenant to Deals (One-to-Many via _tenant_id)
organization_id → deals._tenant_id (logical relationship)
```

### Cascade Behavior
- **DELETE ScanJob**: Cascades to delete all related deals (ON DELETE CASCADE)
- **Multi-tenant Isolation**: All queries should filter by `_tenant_id` to ensure data isolation

---

## 🏢 Multi-Tenant Data Isolation

### Design Pattern

The schema uses **row-level tenant isolation** via the `_tenant_id` column. Every deal record must include a tenant identifier to ensure proper data segregation.

### Tenant Isolation Best Practices

1. **Always filter by `_tenant_id`**: Every query should include tenant filtering
   ```sql
   SELECT * FROM deals WHERE _tenant_id = 'org-12345' AND ...
   ```

2. **Foreign Key Constraints**: Use application-level validation to ensure `_tenant_id` matches `scan_jobs.organization_id`

3. **Index Usage**: The composite index `idx_deals_tenant_scan` enables efficient tenant-scoped queries

4. **Data Access Layer**: Implement a data access layer that automatically appends tenant filters

### Example: Tenant-Scoped Queries

```sql
-- ✅ CORRECT: Tenant-isolated query
SELECT * FROM deals 
WHERE _tenant_id = 'org-12345' 
  AND dealstage = 'closedwon';

-- ❌ INCORRECT: Missing tenant filter (security risk!)
SELECT * FROM deals WHERE dealstage = 'closedwon';

-- ✅ CORRECT: Tenant-scoped aggregation
SELECT dealstage, COUNT(*) as count, SUM(amount) as total
FROM deals 
WHERE _tenant_id = 'org-12345'
  AND createdate >= '2024-01-01'
GROUP BY dealstage;
```

### Tenant Isolation Enforcement

Consider adding a database-level policy (if using PostgreSQL Row Level Security):

```sql
-- Enable Row Level Security
ALTER TABLE deals ENABLE ROW LEVEL SECURITY;

-- Create policy (example - adjust based on your auth system)
CREATE POLICY tenant_isolation_policy ON deals
    FOR ALL
    USING (_tenant_id = current_setting('app.current_tenant_id')::VARCHAR);
```

### Schema Mapping: HubSpot Property Types to PostgreSQL Types

| HubSpot Property Type | PostgreSQL Type | Notes |
|----------------------|----------------|-------|
| `string` | `VARCHAR(n)` | Use appropriate length (500 for names, 50 for IDs) |
| `number` | `NUMERIC(15,2)` | Supports large amounts with 2 decimal places |
| `date` | `TIMESTAMP` | Store as UTC timestamp |
| `datetime` | `TIMESTAMP` | Store as UTC timestamp |
| `enum` | `VARCHAR(100)` | Store enum value as string |
| `bool` | `BOOLEAN` | Direct mapping |
| `object` | `JSONB` | For complex nested objects |
| Custom properties | `JSONB` | Stored in `properties` column |

### ETL Metadata Fields

Every deal record includes these metadata fields:

- **`_extracted_at`**: Timestamp when the record was extracted (used for incremental loads)
- **`_scan_id`**: Identifier of the scan that extracted this record (for scan-based queries)
- **`_tenant_id`**: Organization/tenant identifier (for multi-tenant isolation)

These fields enable:
- **Incremental Loading**: Filter by `_extracted_at` to get only new/updated records
- **Scan Tracking**: Query all deals from a specific scan using `_scan_id`
- **Data Lineage**: Track which scan extracted each deal record
- **Multi-tenant Queries**: Ensure data isolation using `_tenant_id`

---

## 📊 Common Queries

### Basic Scan Management

```sql
-- Get scan job with status
SELECT id, scan_id, status, scan_type, total_items, processed_items 
FROM scan_jobs 
WHERE scan_id = 'your-scan-id';

-- Get active scans
SELECT scan_id, status, started_at, scan_type 
FROM scan_jobs 
WHERE status IN ('running', 'pending') 
ORDER BY created_at DESC;

-- Get scan progress
SELECT 
    scan_id,
    total_items,
    processed_items,
    CASE 
        WHEN total_items > 0 THEN ROUND((processed_items * 100.0 / total_items), 2)
        ELSE 0 
    END as progress_percentage
FROM scan_jobs 
WHERE scan_id = 'your-scan-id';
```

### Deals Management

```sql
-- Get paginated deals for a scan (with tenant isolation)
SELECT 
    id, dealname, amount, dealstage, pipeline, 
    createdate, closedate, dealtype, archived
FROM deals 
WHERE scan_job_id = 'job-id' 
  AND _tenant_id = 'org-12345'
ORDER BY createdate DESC
LIMIT 100 OFFSET 0;

-- Count deals by stage for a tenant
SELECT dealstage, COUNT(*) as count
FROM deals 
WHERE _tenant_id = 'org-12345'
  AND archived = FALSE
GROUP BY dealstage
ORDER BY count DESC;

-- Search deals by name (tenant-isolated)
SELECT id, dealname, amount, dealstage, createdate
FROM deals 
WHERE _tenant_id = 'org-12345'
  AND dealname ILIKE '%enterprise%'
ORDER BY createdate DESC;

-- Get deals by date range (tenant-isolated)
SELECT 
    id, dealname, amount, dealstage, closedate
FROM deals 
WHERE _tenant_id = 'org-12345'
  AND createdate >= '2024-01-01'
  AND createdate < '2024-12-31'
  AND archived = FALSE
ORDER BY createdate DESC;

-- Get deals by pipeline and stage (tenant-isolated)
SELECT 
    pipeline, dealstage, COUNT(*) as count, SUM(amount) as total_amount
FROM deals 
WHERE _tenant_id = 'org-12345'
  AND pipeline = 'default'
  AND archived = FALSE
GROUP BY pipeline, dealstage
ORDER BY pipeline, dealstage;

-- Get closed deals by month (tenant-isolated)
SELECT 
    DATE_TRUNC('month', closedate) as month,
    COUNT(*) as closed_deals,
    SUM(amount) as total_revenue
FROM deals 
WHERE _tenant_id = 'org-12345'
  AND closedate IS NOT NULL
  AND closedate >= '2024-01-01'
GROUP BY DATE_TRUNC('month', closedate)
ORDER BY month DESC;

-- Query custom properties stored in JSONB
SELECT 
    id, dealname, properties->>'custom_field_name' as custom_value
FROM deals 
WHERE _tenant_id = 'org-12345'
  AND properties->>'custom_field_name' IS NOT NULL;
```

### Control Operations

```sql
-- Get scan job status and basic info
SELECT scan_id, status, started_at, completed_at, error_message
FROM scan_jobs 
WHERE scan_id = 'your-scan-id';

-- Cancel a scan (update status)
UPDATE scan_jobs 
SET status = 'cancelled', 
    completed_at = CURRENT_TIMESTAMP,
    error_message = 'Cancelled by user'
WHERE scan_id = 'your-scan-id' 
AND status IN ('pending', 'running');
```

---

## 🛠️ Implementation Examples

### Creating a New Scan Job

```sql
-- Create scan job
INSERT INTO scan_jobs (
    id, scan_id, status, scan_type, config, organization_id, batch_size
) VALUES (
    'uuid-1', 'my-scan-001', 'pending', 'user_extraction', 
    '{"auth": {"token": "..."}, "filters": {...}}', 
    'org-123', 100
);
```

### Adding Deals (ETL Process)

```sql
-- Insert deal records with ETL metadata
INSERT INTO deals (
    id, scan_job_id, _scan_id, _tenant_id, _extracted_at,
    dealname, amount, dealstage, pipeline, createdate, closedate,
    dealtype, hubspot_owner_id, description, deal_currency_code,
    hs_next_step, hs_priority, archived, properties,
    hubspot_created_at, hubspot_updated_at
) VALUES 
(
    '1234567890', 
    'job-uuid-1', 
    'hubspot-deals-scan-2025-001',
    'org-12345',
    CURRENT_TIMESTAMP,
    'Q1 Enterprise Deal',
    50000.00,
    'appointmentscheduled',
    'default',
    '2024-01-15 10:00:00',
    NULL,
    'newbusiness',
    '12345678',
    'Large enterprise customer deal',
    'USD',
    'Schedule discovery call',
    'high',
    FALSE,
    '{"custom_field": "value"}'::jsonb,
    '2024-01-15 10:00:00',
    '2024-01-15 12:30:00'
),
(
    '0987654321',
    'job-uuid-1',
    'hubspot-deals-scan-2025-001',
    'org-12345',
    CURRENT_TIMESTAMP,
    'Enterprise Renewal',
    75000.00,
    'closedwon',
    'default',
    '2024-01-10 08:00:00',
    '2024-02-01 17:00:00',
    'existingbusiness',
    '12345678',
    NULL,
    'USD',
    NULL,
    'medium',
    FALSE,
    NULL,
    '2024-01-10 08:00:00',
    '2024-02-01 17:00:00'
);

-- Update scan job progress
UPDATE scan_jobs 
SET processed_items = processed_items + 2,
    updated_at = CURRENT_TIMESTAMP
WHERE id = 'job-uuid-1';

-- Upsert pattern (for incremental updates)
INSERT INTO deals (
    id, scan_job_id, _scan_id, _tenant_id, _extracted_at,
    dealname, amount, dealstage, pipeline, createdate, closedate,
    archived, properties, hubspot_updated_at
)
VALUES (
    '1234567890',
    'job-uuid-1',
    'hubspot-deals-scan-2025-001',
    'org-12345',
    CURRENT_TIMESTAMP,
    'Q1 Enterprise Deal',
    50000.00,
    'appointmentscheduled',
    'default',
    '2024-01-15 10:00:00',
    NULL,
    FALSE,
    '{"custom_field": "value"}'::jsonb,
    '2024-01-15 12:30:00'
)
ON CONFLICT (id) 
DO UPDATE SET
    amount = EXCLUDED.amount,
    dealstage = EXCLUDED.dealstage,
    closedate = EXCLUDED.closedate,
    archived = EXCLUDED.archived,
    properties = EXCLUDED.properties,
    hubspot_updated_at = EXCLUDED.hubspot_updated_at,
    _extracted_at = EXCLUDED._extracted_at,
    updated_at = CURRENT_TIMESTAMP;
```

### Status Updates

```sql
-- Start scan
UPDATE scan_jobs 
SET status = 'running', 
    started_at = CURRENT_TIMESTAMP 
WHERE scan_id = 'my-scan-001';

-- Complete scan
UPDATE scan_jobs 
SET status = 'completed', 
    completed_at = CURRENT_TIMESTAMP,
    success_rate = CASE 
        WHEN total_items > 0 THEN ROUND(((total_items - failed_items) * 100.0 / total_items), 2)::TEXT || '%'
        ELSE '100%' 
    END
WHERE scan_id = 'my-scan-001';
```

---

## 📈 Performance Optimization

### Index Strategy

The schema includes comprehensive indexes optimized for common query patterns:

1. **Tenant Isolation Queries**: `idx_deals_tenant_id`, `idx_deals_tenant_scan`
2. **Date Range Queries**: `idx_deals_create_date`, `idx_deals_close_date`, `idx_deals_tenant_date`
3. **Stage/Pipeline Analysis**: `idx_deals_stage`, `idx_deals_pipeline`, `idx_deals_tenant_stage`, `idx_deals_tenant_pipeline`
4. **Scan Tracking**: `idx_deals_scan_id`, `idx_deals_scan_job_id`
5. **Custom Properties**: `idx_deals_properties_gin` (GIN index for JSONB queries)

### Query Performance Tips

1. **Always use tenant filters**: Ensure all queries include `_tenant_id` for proper isolation and index usage
2. **Use partial indexes**: The schema uses partial indexes (WHERE clauses) for better performance on non-null values
3. **Leverage composite indexes**: Use `_tenant_id` + other columns for multi-tenant filtered queries
4. **JSONB queries**: Use GIN index for efficient custom property queries

### Monitoring Query Performance

```sql
-- Analyze query plans
EXPLAIN ANALYZE
SELECT * FROM deals 
WHERE _tenant_id = 'org-12345' 
  AND dealstage = 'closedwon'
  AND closedate >= '2024-01-01';

-- Check index usage
SELECT 
    schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes 
WHERE tablename = 'deals'
ORDER BY idx_scan DESC;
```

---

## 📈 Performance Considerations

### Indexing Strategy
- **Primary Operations**: Index on `scan_id`, `status`, and `created_at`
- **Filtering**: Index on `organization_id`, `scan_type`, `result_type`
- **Pagination**: Composite indexes on frequently queried column combinations
- **Foreign Keys**: Always index foreign key columns

### Data Retention
```sql
-- Archive completed scans older than 90 days
CREATE TABLE scan_jobs_archive AS SELECT * FROM scan_jobs WHERE FALSE;

-- Move old data
INSERT INTO scan_jobs_archive 
SELECT * FROM scan_jobs 
WHERE status = 'completed' 
AND completed_at < CURRENT_DATE - INTERVAL '90 days';

-- Clean up
DELETE FROM scan_jobs 
WHERE status = 'completed' 
AND completed_at < CURRENT_DATE - INTERVAL '90 days';
```

### Large Result Sets (Partitioning)

For very large datasets, consider partitioning the deals table by tenant or date:

```sql
-- Partition deals table by tenant_id for very large multi-tenant datasets
CREATE TABLE deals (
    -- columns as defined above
) PARTITION BY HASH (_tenant_id);

-- Create partitions (adjust number based on tenant count)
CREATE TABLE deals_p0 PARTITION OF deals FOR VALUES WITH (modulus 4, remainder 0);
CREATE TABLE deals_p1 PARTITION OF deals FOR VALUES WITH (modulus 4, remainder 1);
CREATE TABLE deals_p2 PARTITION OF deals FOR VALUES WITH (modulus 4, remainder 2);
CREATE TABLE deals_p3 PARTITION OF deals FOR VALUES WITH (modulus 4, remainder 3);

-- Alternatively, partition by date for time-series analysis
CREATE TABLE deals (
    -- columns as defined above
) PARTITION BY RANGE (createdate);

-- Create monthly partitions
CREATE TABLE deals_2024_01 PARTITION OF deals 
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
CREATE TABLE deals_2024_02 PARTITION OF deals 
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
-- etc.
```

---

## 🛡️ Data Integrity

### Constraints
```sql
-- Ensure valid status values
ALTER TABLE scan_jobs ADD CONSTRAINT check_valid_status 
CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled'));

-- Ensure valid deal stage values (example - adjust based on your stages)
ALTER TABLE deals ADD CONSTRAINT check_valid_stage 
CHECK (dealstage IS NULL OR dealstage IN ('appointmentscheduled', 'qualifiedtobuy', 'presentationscheduled', 'decisionmakerboughtin', 'contractsent', 'closedwon', 'closedlost'));

-- Ensure amount is non-negative
ALTER TABLE deals ADD CONSTRAINT check_non_negative_amount 
CHECK (amount IS NULL OR amount >= 0);

-- Ensure positive values
ALTER TABLE scan_jobs ADD CONSTRAINT check_positive_counts 
CHECK (total_items >= 0 AND processed_items >= 0 AND failed_items >= 0);
```

### Triggers
```sql
-- Auto-update timestamps
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_scan_jobs_updated_at 
    BEFORE UPDATE ON scan_jobs 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_deals_updated_at 
    BEFORE UPDATE ON deals 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
```

---

### Usage Guidelines

### Best Practices
1. **Use appropriate batch sizes** for your data volume to manage memory and performance
2. **Implement proper error handling** and store error details in `error_message`
3. **Regular cleanup** of old scan jobs and results based on retention policies
4. **Monitor scan progress** using the progress tracking fields (`total_items`, `processed_items`)
5. **Use JSON config** to store flexible scan parameters and authentication details

### Common Patterns
- **Progress Tracking**: Update `processed_items` and `failed_items` as scan progresses
- **Error Recovery**: Store detailed error information in `error_message` field
- **Flexible Configuration**: Use JSON `config` field for scan parameters, auth details, filters
- **Status Management**: Use clear status transitions (pending → running → completed/failed/cancelled)
- **Data Organization**: Use meaningful `scan_id` values for easy identification

---

**Database Schema Version**: 1.0  
**Last Updated**: 2025-01-15  
**Compatible With**: PostgreSQL 12+  
**Tested On**: PostgreSQL 14, PostgreSQL 15