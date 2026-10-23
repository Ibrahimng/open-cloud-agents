# PromQL Golden Signals Cheat Sheet

## 1. HTTP Services
- **p99 Latency:**
  `histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket{job="app"}[5m])) by (le))`
- **Requests Per Second (RPS):**
  `sum(rate(http_requests_total{job="app"}[2m])) by (handler)`
- **Error Percentage (5xx):**
  `(sum(rate(http_requests_total{job="app", status=~"5.."}[2m])) / sum(rate(http_requests_total{job="app"}[2m]))) * 100`

## 2. PostgreSQL Databases
- **Active Connections:**
  `sum(pg_stat_activity_count{datname="prod_db"})`
- **Cache Hit Ratio (Goal > 99%):**
  `sum(rate(pg_stat_database_blks_hit{datname="prod_db"}[5m])) / (sum(rate(pg_stat_database_blks_hit{datname="prod_db"}[5m])) + sum(rate(pg_stat_database_blks_read{datname="prod_db"}[5m]))) * 100`
- **Deadlocks Total:**
  `rate(pg_stat_database_deadlocks{datname="prod_db"}[5m])`

## 3. Kubernetes Infrastructure
- **Pod CPU Throttling Percentage:**
  `sum(rate(container_cpu_cfs_throttled_periods_total[5m])) / sum(rate(container_cpu_cfs_periods_total[5m])) * 100`
- **OOM Kill Count:**
  `sum(kube_pod_container_status_terminated_reason{reason="OOMKilled"}) by (namespace, pod)`

