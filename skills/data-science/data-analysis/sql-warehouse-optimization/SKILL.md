---
name: sql-warehouse-optimization
description: Optimize analytical SQL queries for BigQuery, Snowflake, and Redshift through partitioning, clustering, pruning unneeded columns, and eliminating cross-joins.
---

# Analytical SQL & Cloud Data Warehouse Optimization

## 1. Partitioning & Clustering (BigQuery / Snowflake)
- **Always partition by date/timestamp** (e.g. `event_timestamp`) to prune scanned byte volume.
- **Cluster by high-cardinality filter fields** (e.g. `customer_id`, `region`, `status`).

### Optimized Table Definition (BigQuery DDL Example)
```sql
CREATE OR REPLACE TABLE `analytics_prod.events_partitioned`
PARTITION BY DATE(event_timestamp)
CLUSTER BY customer_id, event_type
AS
SELECT * FROM `analytics_prod.raw_events`;
```

## 2. Query Anti-Patterns to Eliminate
- **Ban `SELECT *`**: Reading unneeded columns inflates BigQuery slot time and egress costs. Always list required columns explicitly.
- **Filter Early (Pushdown Predicates)**: Apply `WHERE` filters before `JOIN` operations or in CTEs.
- **Avoid Cross Joins**: Never join without explicit `ON` join keys unless computing a Cartesian product intentionally.
- **Approximate Aggregations for Large Data**: Use `APPROX_COUNT_DISTINCT()` instead of `COUNT(DISTINCT)` on massive datasets (reduces query runtime by 80%+ with < 1% error).

## 3. Query Execution Plan Profiling
Before deploying an analytical query to production pipelines:
```sql
-- BigQuery Execution Plan check: Look for stages with high Slot Time or heavy repartitioning
EXPLAIN
SELECT 
    customer_id, 
    COUNT(1) as total_events
FROM `analytics_prod.events_partitioned`
WHERE event_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY 1;
```
