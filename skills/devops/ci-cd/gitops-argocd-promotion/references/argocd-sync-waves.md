# ArgoCD Sync Waves & Progressive Delivery Reference

## Sync Wave Ordering
ArgoCD sync waves allow orchestrating dependent resource applications using the `argocd.argoproj.io/sync-wave` annotation:

| Wave | Resources | Purpose |
|---|---|---|
| **Wave -2** | Namespaces, CRDs | Base cluster requirements |
| **Wave -1** | Secrets, ConfigMaps, RBAC ServiceAccounts | Dependencies required before pods start |
| **Wave 0** | Database migrations (Jobs with `helm.sh/hook` or Sync Hook) | Schema migrations must finish before app code deploys |
| **Wave 1** | Deployments, StatefulSets, Services | Core application runtime |
| **Wave 2** | Ingress, Route53 DNS records, IngressRoutes | Exposing traffic after application pods pass readiness |

## Hook Example (Database Migration Job)
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: schema-migration-v2
  annotations:
    argocd.argoproj.io/hook: PreSync
    argocd.argoproj.io/hook-delete-policy: HookSucceeded
spec:
  template:
    spec:
      containers:
        - name: migrate
          image: app-migrator:sha-12345
      restartPolicy: Never
```

