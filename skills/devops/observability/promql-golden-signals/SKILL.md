---
name: promql-golden-signals
description: Author performant PromQL queries and Prometheus alert rules targeting the Four Golden Signals (Latency, Traffic, Errors, Saturation) and multi-window SLI/SLO burn rates.
---

# PromQL & The Four Golden Signals

## The Four Golden Signals in PromQL

### 1. Latency (p99 & p95 Duration)
Measures request turnaround time in seconds:
```promql
# p99 Latency over 5m window
histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket{job="api-service"}[5m])) by (le))
```

### 2. Traffic (Throughput / Requests Per Second)
Measures system demand:
```promql
sum(rate(http_requests_total{job="api-service"}[2m])) by (handler)
```

### 3. Errors (HTTP 5xx Failure Rate)
Calculates error percentage:
```promql
sum(rate(http_requests_total{job="api-service", status=~"5.."}[2m]))
/
sum(rate(http_requests_total{job="api-service"}[2m])) * 100
```

### 4. Saturation (CPU / Memory Resource Pressure)
Measures how full the service runtime is:
```promql
# Pod memory saturation against limits
sum(container_memory_working_set_bytes{container!="POD", container!=""}) by (pod)
/
sum(kube_pod_container_resource_limits{resource="memory"}) by (pod) * 100
```

## Production Prometheus Alert Rule Example
```yaml
groups:
  - name: api-sli-alerts
    rules:
      - alert: High5xxErrorRate
        expr: |
          (sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))) > 0.01
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "API Service 5xx Error Rate > 1% (current: {{ $value | humanizePercentage }})"
```
