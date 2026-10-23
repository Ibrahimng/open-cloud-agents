# HikariCP Connection Pool Sizing & Tuning Cheat Sheet

## Pool Sizing Formula (PostgreSQL / MySQL)
```text
connections = ((core_count * 2) + effective_spindle_count)
```
- E.g. For a 4-core database server with an SSD (1 spindle equivalent):
  `connections = (4 * 2) + 1 = 9 to 10 connections`.
- **Counter-Intuitive Truth:** Adding hundreds of connections to a database slows it down due to context switching and lock thrashing. Keep pools small (10–20 connections per instance) and scale compute horizontally.

## Recommended `application.yml` Parameters
```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 15
      minimum-idle: 5
      idle-timeout: 300000        # 5 minutes
      max-lifetime: 1800000       # 30 minutes (must be shorter than firewall/NAT TCP timeout)
      connection-timeout: 20000   # 20 seconds
      leak-detection-threshold: 5000 # Logs warning if thread holds connection > 5 seconds
```

