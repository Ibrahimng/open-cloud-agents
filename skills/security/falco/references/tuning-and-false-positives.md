# Falco Rule Tuning, Exceptions & False Positive Mitigation

High-density Kubernetes clusters generate millions of system calls per minute. This guide provides best practices for eliminating noise, scoping exceptions, and tuning Falco for maximum signal-to-noise ratio.

---

## 1. Local Overrides with `falco_rules.local.yaml`

Never modify upstream rules directly in `falco_rules.yaml`. Upstream updates overwrite changes. Instead, place modifications and custom macros in `falco_rules.local.yaml`.

```yaml
# In /etc/falco/falco_rules.local.yaml

# 1. Extend upstream macros
- macro: user_known_shell_applications
  condition: (proc.pname in (jenkins-agent, gitlab-runner) and k8s.ns.name == "ci-runners")

# 2. Append exceptions directly to upstream rules
- rule: Terminal Shell Spawned in Container
  append: true
  condition: and not user_known_shell_applications
```

---

## 2. Structured Exceptions Syntax

Falco supports structured `exceptions` within rule declarations. This approach is cleaner and less error-prone than sprawling `and not ...` boolean chains:

```yaml
- rule: Write below etc
  desc: Alerts on writes to /etc
  condition: open_write and fd.name startswith /etc
  output: File below /etc opened for writing (file=%fd.name proc=%proc.name)
  priority: ERROR
  exceptions:
    - name: proc_and_file_whitelist
      fields: [proc.name, fd.name]
      comps: [in, startswith]
      values:
        - [nginx, /etc/nginx/conf.d]
        - [fluentbit, /etc/fluentbit/parsers.conf]
```

---

## 3. Profiling & Buffer Optimization

When running in high-load environments, monitor dropped events:

```bash
# Check Falco drop statistics
curl -s http://localhost:8765/metrics | grep falco_drops
```

### Optimization Knobs (`/etc/falco/falco.yaml`)

```yaml
# Increase eBPF ring buffer size per CPU core (default is 8MB)
modern_bpf:
  cpus_for_each_buffer: 2
  buffer_dim_mb: 16

# Rate limiting for alerts (prevents log saturation during incident spikes)
outputs:
  rate: 100
  max_burst: 1000
```
