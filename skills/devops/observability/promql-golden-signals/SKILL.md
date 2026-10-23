---
name: promql-golden-signals
description: Author performant PromQL queries and Prometheus alert rules targeting the Four Golden Signals (Latency, Traffic, Errors, Saturation) based on real-world outage postmortems.
---

# PromQL & The Four Golden Signals

## Purpose & Scope
This skill provides real-time PromQL exploration queries and alerting rules to diagnose distributed systems incidents before they escalate into global outages.

---

## Real-Life Production Incident Case: The Connection Pool Exhaustion & Thread Starvation Storm

### Background & What Happened
At 14:02 UTC, user-facing latency on an API gateway climbed from 45ms to 12,000ms. CPU usage on application pods remained low (< 25%), masking the root cause from standard autoscalers. Pods remained healthy and traffic volume was steady. 
Standard alerts failed to fire because the error rate was under 0.5% (requests were hanging until client gateway timeouts at 30 seconds).

### Real-Time Live PromQL Exploration Sequence

#### 1. Quantile Latency Divergence Inspection
Compare median (p50) against tail latency (p95, p99) to identify whether all users are slow or only specific queries:
```promql
# Tail latency divergence
histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket{service="billing"}[2m])) by (le))
-
histogram_quantile(0.50, sum(rate(http_request_duration_seconds_bucket{service="billing"}[2m])) by (le))
```
*Result:* p50 was 30ms, while p99 was 29,800ms. A subset of database-dependent endpoints was hanging.

#### 2. Downstream Database Connection Pool Saturation
Inspect connection pool saturation across application instances:
```promql
# Connection pool utilization ratio
sum(hikari_pool_active_connections{service="billing"}) by (pod)
/
sum(hikari_pool_max_connections{service="billing"}) by (pod) * 100
```
*Result:* 100% of pods had saturated connection pools (10/10 active connections locked).

#### 3. Correlate with Database Lock Contention
```promql
sum(rate(postgresql_locks_acquired_total{mode="ExclusiveLock"}[5m])) by (datname)
```
*Root Cause:* An unindexed query in a new migration held an exclusive table lock, causing all application threads to wait indefinitely for database connections.

---

## The Four Golden Signals Live Diagnostic Query Sheet

| Signal | Production PromQL Query | Critical Warning Threshold |
|---|---|---|
| **Latency (p99)** | `histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))` | > 500ms for REST, > 100ms for gRPC |
| **Traffic** | `sum(rate(http_requests_total[2m])) by (service)` | > 30% sudden drop or 200% sudden surge |
| **Errors** | `(sum(rate(http_requests_total{status=~"5.."}[2m])) / sum(rate(http_requests_total[2m]))) * 100` | > 1.0% error rate |
| **Saturation** | `sum(container_memory_working_set_bytes) by (pod) / sum(kube_pod_container_resource_limits{resource="memory"}) by (pod)` | > 85% memory or connection limit |

---

## Continuous Self-Knowledge Enhancement Loop

When the SRE agent resolves a silent failure mode:
1. **Identify Alerting Gaps:** (e.g. "We only monitored HTTP 5xx errors; we had no alert for thread pool saturation or p99 tail latency divergence.").
2. **Draft New Multi-Window Burn Alert:** Automatically author an alert rule checking latency percentile divergence.
3. **Commit Rule into Observability Repository:** Propose the updated Prometheus rule directly to `skills/devops/observability/promql-golden-signals/SKILL.md` so the team's monitoring continuously compounds.
