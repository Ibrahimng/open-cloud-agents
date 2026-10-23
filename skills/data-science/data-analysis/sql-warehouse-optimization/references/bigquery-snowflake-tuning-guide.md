# BigQuery & Snowflake Cost & Performance Optimization Guide

## 1. Partitioning Strategy
- **Daily Partitioning:** For event tables receiving > 10GB/day, partition by `DATE(event_timestamp)`.
- **Partition Expiration:** Configure 90-day partition expiration for staging tables to prevent silent storage bloat.
- **Partition Filter Requirement:** Mandate `require_partition_filter = true` on massive tables:
  ```sql
  ALTER TABLE analytics.events SET OPTIONS (require_partition_filter = true);
  ```

## 2. Clustering vs Secondary Indexing
- Choose up to 4 columns ordered by filtering frequency:
  1. `tenant_id` / `customer_id` (Equality filter)
  2. `event_type` (Categorical filter)
  3. `user_id` (Join key)

## 3. High-Cost SQL Anti-Patterns
- **Repeated Subqueries:** Use Common Table Expressions (CTEs) or temporary tables rather than repeating the same subquery across multiple joins.
- **`COUNT(DISTINCT)` on High Cardinality:** Replace with HyperLogLog++ approximate aggregation:
  `APPROX_COUNT_DISTINCT(user_id)` (Reduces memory pressure by 90%+ with 99% accuracy).

