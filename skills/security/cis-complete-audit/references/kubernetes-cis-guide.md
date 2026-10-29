# CIS Kubernetes Benchmark Audit Guide (v1.9)

This guide covers the controls, flags, and admission checks mandated by the CIS Kubernetes Benchmark across the Control Plane, etcd, Worker Nodes (Kubelet), and Workload Policies.

---

## 1. Control Plane Components

### 1.1 Kubernetes API Server (`kube-apiserver`)

Manifest location: `/etc/kubernetes/manifests/kube-apiserver.yaml`

| Benchmark ID | Parameter / Flag | Recommended Setting | Rationale |
|---|---|---|---|
| **K8S 1.2.1** | `--anonymous-auth` | `false` | Disables unauthenticated access to the API server endpoints. |
| **K8S 1.2.2** | `--basic-auth-file` | *Do not set* | Deprecated plaintext username/password credentials. |
| **K8S 1.2.3** | `--token-auth-file` | *Do not set* | Static bearer token files cannot be rotated dynamically without restarting the API server. |
| **K8S 1.2.7** | `--authorization-mode` | Must include `Node,RBAC` | Restricts kubelet API privileges to its own node resources and enforces RBAC. |
| **K8S 1.2.14** | `--enable-admission-plugins` | Must include `NodeRestriction,PodSecurity` | Limits what nodes can modify and enforces Pod Security Standards. |
| **K8S 1.2.16** | `--secure-port` | `6443` (not `0`) | Enforces TLS encryption for all API server network communications. |
| **K8S 1.2.19** | `--profiling` | `false` | Prevents profiling endpoint `/debug/pprof` memory/goroutine information disclosure. |
| **K8S 1.2.21** | `--audit-log-path` | `/var/log/k8s-audit.log` | Records all cluster requests and state mutations. |
| **K8S 1.2.22** | `--audit-log-maxage` | `30` | Ensures audit logs are retained for at least 30 days. |

### 1.2 Controller Manager & Scheduler

- **Controller Manager (`kube-controller-manager`):**
    - `--terminated-pod-gc-threshold=12500` (avoids resource starvation from dead pods).
    - `--use-service-account-credentials=true` (ensures individual service account credentials per controller).
    - `--root-ca-file` pointing to valid CA certificate bundle.
- **Scheduler (`kube-scheduler`):**
    - `--profiling=false`

---

## 2. etcd Key-Value Store
Manifest location: `/etc/kubernetes/manifests/etcd.yaml`

| Benchmark ID | Parameter / Flag | Recommended Setting | Rationale |
|---|---|---|---|
| **K8S 2.1** | `--cert-file` & `--key-file` | Set to valid TLS cert/key paths | Enforces TLS on client connections to etcd. |
| **K8S 2.2** | `--client-cert-auth` | `true` | Requires mutual TLS authentication for all client requests. |
| **K8S 2.3** | `--peer-cert-file` & `--peer-key-file` | Set to valid peer TLS paths | Secures inter-etcd node replication traffic. |
| **K8S 2.4** | `--peer-client-cert-auth` | `true` | Requires mutual TLS authentication between etcd cluster members. |
| **K8S 2.7** | Encryption at Rest | `EncryptionConfiguration` with KMS provider | Protects secrets in etcd database from offline extraction. |

---

## 3. Worker Node Security (`kubelet`)
Configuration file: `/var/lib/kubelet/config.yaml` or `/etc/kubernetes/kubelet.conf`

| Benchmark ID | Parameter | Recommended Setting | Rationale |
|---|---|---|---|
| **K8S 4.2.1** | `authentication.anonymous.enabled` | `false` | Rejects unauthenticated requests to the kubelet HTTP API. |
| **K8S 4.2.2** | `authorization.mode` | `Webhook` | Delegates kubelet authorization decisions to the API server via RBAC. |
| **K8S 4.2.3** | `authentication.x509.clientCAFile` | Valid CA path | Enforces client certificate validation. |
| **K8S 4.2.4** | `readOnlyPort` | `0` | Disables unauthenticated read-only port 10255. |
| **K8S 4.2.6** | `protectKernelDefaults` | `true` | Prevents kubelet from overriding kernel tuning parameters. |
| **K8S 4.2.7** | `makeIPTablesChains` | `true` | Ensures kubelet creates required iptables chains. |
| **K8S 4.2.10** | `streamingConnectionIdleTimeout` | `4h` | Terminates abandoned exec/port-forward sessions. |

---

## 4. Workload Security & Pod Security Standards (PSS)

Enforce labels at the namespace level to mandate the CIS `restricted` profile:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production-apps
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: latest
    pod-security.kubernetes.io/warn: restricted
    pod-security.kubernetes.io/audit: restricted
```

### Pod Security Policy Invariants:
1. `privileged: false` (Zero privileged containers).
2. `allowPrivilegeEscalation: false` (No new privileges).
3. `readOnlyRootFilesystem: true` (Immutable container filesystem).
4. `runAsNonRoot: true` (Container UID must be $> 0$).
5. `drop: ["ALL"]` in `capabilities` (Drop all default Linux capabilities; add back only needed ones e.g. `NET_BIND_SERVICE`).
6. `hostPID: false`, `hostIPC: false`, `hostNetwork: false`.

---

## 5. Audit Commands

```bash
# Verify API server anonymous auth flag
kubectl get pods -n kube-system -l component=kube-apiserver -o jsonpath='{.items[*].spec.containers[*].command}' | grep -o -- '--anonymous-auth=[^ ]*'

# Check kubelet configuration
curl -s --cacert /var/lib/kubelet/pki/kubelet.crt https://localhost:10250/configz | jq .kubeletconfig.authentication.anonymous

# Audit cluster for privileged pods
kubectl get pods --all-namespaces -o jsonpath='{range .items[*]}{.metadata.namespace}{"\t"}{.metadata.name}{"\t"}{range .spec.containers[*]}{.securityContext.privileged}{" "}{end}{"\n"}{end}' | grep true
```
