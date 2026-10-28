# CIS Docker & Container Runtime Benchmark Matrix

This reference details daemon settings, container runtime flags, and security contexts required by the CIS Docker Community Edition Benchmark (v1.6).

---

## 1. Docker Daemon Hardening (`/etc/docker/daemon.json`)

```json
{
  "icc": false,
  "userns-remap": "default",
  "live-restore": true,
  "no-new-privileges": true,
  "userland-proxy": false,
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "50m",
    "max-file": "5"
  },
  "storage-driver": "overlay2",
  "seccomp-profile": "/etc/docker/seccomp-default.json",
  "tlsverify": true,
  "tlscacert": "/etc/docker/ca.pem",
  "tlscert": "/etc/docker/server-cert.pem",
  "tlskey": "/etc/docker/server-key.pem"
}
```

### Critical Daemon Invariants:
1. `"icc": false`: Disables default inter-container communication on the docker0 bridge, forcing container communication through explicit user-defined bridge networks.
2. `"userns-remap": "default"`: Maps container root UID 0 to an unprivileged high UID on the host (e.g. UID 100000), preventing root container escape exploits from gaining host root access.
3. `"no-new-privileges": true`: Prevents processes inside containers from acquiring additional privileges via `setuid` or `setgid` binaries.
4. `"live-restore": true`: Keeps containers running during daemon downtime, updates, or crashes.

---

## 2. Container Runtime Security Controls

| Benchmark ID | Rule Title | Runtime Flag | Verification Command |
|---|---|---|---|
| **DOCKER 4.1** | Restrict AppArmor profile | `--security-opt apparmor=docker-default` | `docker inspect --format '{{ .AppArmorProfile }}' <ID>` |
| **DOCKER 4.2** | Verify SELinux security options | `--security-opt label=level:s0:c100,c200` | `docker inspect --format '{{ .HostConfig.SecurityOpt }}' <ID>` |
| **DOCKER 5.1** | Do not disable default AppArmor profile | Ensure no `--security-opt apparmor=unconfined` | Check docker run command / spec |
| **DOCKER 5.2** | Do not disable default Seccomp profile | Ensure no `--security-opt seccomp=unconfined` | `docker inspect --format '{{ .HostConfig.SecurityOpt }}' <ID>` |
| **DOCKER 5.3** | Do not run containers with `--privileged` flag | Avoid `--privileged` | `docker inspect --format '{{ .HostConfig.Privileged }}' <ID>` (Must be `false`) |
| **DOCKER 5.4** | Do not mount sensitive host system directories | Avoid mounting `/`, `/boot`, `/dev`, `/etc`, `/lib`, `/proc`, `/sys`, `/usr` | `docker inspect --format '{{ json .Mounts }}' <ID>` |
| **DOCKER 5.7** | Do not map privileged ports below 1024 | Port binding $\ge 1024$ | `docker inspect --format '{{ json .NetworkSettings.Ports }}' <ID>` |
| **DOCKER 5.9** | Do not share host network namespace | Avoid `--net=host` | `docker inspect --format '{{ .HostConfig.NetworkMode }}' <ID>` (Must not be `host`) |
| **DOCKER 5.12** | Mount container root filesystem as read-only | `--read-only` | `docker inspect --format '{{ .HostConfig.ReadonlyRootfs }}' <ID>` (Must be `true`) |
| **DOCKER 5.14** | Ensure `no-new-privileges` is set | `--security-opt no-new-privileges:true` | `docker inspect --format '{{ .HostConfig.SecurityOpt }}' <ID>` |
| **DOCKER 5.25** | Restrict container memory usage | `--memory 512m` | `docker inspect --format '{{ .HostConfig.Memory }}' <ID>` |
| **DOCKER 5.26** | Restrict container CPU usage | `--cpus 1.5` | `docker inspect --format '{{ .HostConfig.NanoCpus }}' <ID>` |

---

## 3. Docker Content Trust & Image Integrity

Enforce image signing and verification via Notary / Cosign:

```bash
# Enable Docker Content Trust in environment
export DOCKER_CONTENT_TRUST=1

# Pulling an unsigned image will fail with:
# Error: remote trust data does not exist for docker.io/...
docker pull my-registry.internal/app:1.0.0
```
