# Sysdig OSS Command & Chisel Cheatsheet

This reference provides filter syntax, capture options, and built-in chisels for the open-source `sysdig` command-line utility.

---

## 1. Core CLI Options

```bash
# Capture events to a trace file (.scap)
sysdig -w capture.scap

# Read and filter from a capture file
sysdig -r capture.scap "proc.name=bash"

# Truncate buffer size for packet/payload inspection
sysdig -s 2048 -A -r capture.scap

# Output format customization
sysdig -p "%12user.name %20proc.name %16container.name %fd.name"
```

---

## 2. Essential Chisel Utilities

Chisels are modular Lua scripts extending Sysdig to perform aggregated analytics:

| Category | Chisel Command | Description |
|---|---|---|
| **User Activity** | `sysdig -c spy_users` | Streams interactive user commands and shell keystrokes in real time. |
| **Processes** | `sysdig -c topprocs_cpu` | Ranks processes consuming the highest host CPU. |
| **Processes** | `sysdig -c topprocs_errors` | Identifies processes triggering system call errors (e.g. `EACCES`, `ENOENT`). |
| **Containers** | `sysdig -c topcontainers_cpu` | Ranks containers by CPU consumption. |
| **Containers** | `sysdig -c topcontainers_net` | Ranks containers by network bandwidth consumption. |
| **Network** | `sysdig -c netflow` | Visualizes network connections and bandwidth between IPs and ports. |
| **Network** | `sysdig -c topprocs_net` | Identifies processes generating the most network traffic. |
| **I/O & Payloads** | `sysdig -c echo_fds` | Prints ASCII payload data transferred across network or file descriptors. |
| **File Access** | `sysdig -c fdbytes_by fd.filename` | Displays byte I/O aggregated by filename. |
| **File Access** | `sysdig -c list_open_fds` | Lists open file descriptors across all running processes. |

---

## 3. High-Value Sysdig Filter Expressions

### Process & Container Filters
```bash
# Detect interactive shells launched inside any container
sysdig "container.id != host and (proc.name in (bash, sh, zsh))"

# Detect processes spawned by an unexpected parent
sysdig "proc.name=curl and proc.pname!=java"

# Filter by Kubernetes namespace and pod
sysdig "k8s.ns.name=production and k8s.pod.name contains payment"
```

### Filesystem & I/O Filters
```bash
# Monitor writes to sensitive system directories
sysdig "evt.is_open_write=true and (fd.name startswith /etc or fd.name startswith /usr/bin)"

# Detect reading of private SSH keys
sysdig "evt.type=open and fd.name contains id_rsa"

# Detect file deletions across containers
sysdig "evt.type in (unlink, unlinkat) and container.id != host"
```

### Network Filters
```bash
# Detect network connections to external IP ranges (excluding RFC 1918)
sysdig "evt.type=connect and not (fd.dip startswith 10. or fd.dip startswith 172.16. or fd.dip startswith 192.168. or fd.dip=127.0.0.1)"

# Capture HTTP requests with response status codes
sysdig -s 2000 -A -c echo_fds "fd.port=80 or fd.port=443"
```
