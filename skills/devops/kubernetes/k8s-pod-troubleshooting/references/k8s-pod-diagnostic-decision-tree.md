# Kubernetes Pod Diagnostic Decision Tree & Exit Codes

```text
                                  [Pod Unhealthy]
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        ▼                                ▼                                ▼
[Exit Code 137]                  [Exit Code 1 / 2]                [Exit Code 143]
  OOMKilled                        Application Error                Graceful SIGTERM
  - Pod exceeded memory limit      - Uncaught exception/panic       - Teardown initiated by K8s
  - Action: Check container limits - Action: kubectl logs --previous - Action: Check terminationGracePeriod
                                         │
        ┌────────────────────────────────┴────────────────────────────────┐
        ▼                                                                 ▼
[Pending Status]                                                 [ImagePullBackOff]
  - Insufficient CPU/Memory on node pool                           - Registry authentication failure
  - PVC bound to different availability zone                       - Image tag does not exist
  - Action: kubectl describe pod | grep -A 5 Events               - Action: verify imagePullSecrets
```

## Exit Code Reference Table

| Exit Code | Signal / Name | Root Cause | Immediate Action |
|---|---|---|---|
| **`137`** | `SIGKILL` | **OOMKilled** (Memory limit exceeded) or container killed by host kernel. | Run `kubectl describe pod`, inspect memory limits, collect memory profile. |
| **`139`** | `SIGSEGV` | Segmentation fault in native binary or C-extension. | Inspect core dump, check shared library architecture (x86 vs ARM). |
| **`143`** | `SIGTERM` | Graceful termination signal sent during pod eviction or rollout. | Normal during deploy; if unexpected, check node autoscaler / spot termination. |
| **`1`** | General Error | Application syntax error, uncaught exception, or missing env var. | Check `kubectl logs <pod> --previous`. |
| **`2`** | Misuse of Shell | Missing command executable or invalid shell arguments in `command: []`. | Verify entrypoint binary exists in the container image. |
