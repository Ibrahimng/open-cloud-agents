---
name: gitops-argocd-promotion
description: Automate progressive multi-environment promotion (dev -> uat -> prod) using ArgoCD, Kustomize overlays, automated drift detection, and canary verification.
---

# GitOps & ArgoCD Environment Promotion

## Architecture Overview
Follow a decoupled repository structure:
- **Application Repo:** Contains source code, unit tests, and Dockerfiles. On merge to `main`, builds container and tags image SHA.
- **Config / GitOps Repo:** Contains Kubernetes manifests managed by environment overlays (`base/`, `overlays/dev/`, `overlays/uat/`, `overlays/prod/`).

## Promotion Progression
```text
[Commit to App Repo]
       │
       ▼
1. Build & Push Image (`app:sha-abc1234`)
       │
       ▼
2. Update `overlays/dev/kustomization.yaml` ➔ ArgoCD Auto-Sync
       │
       ▼ (Automated Integration Tests Pass)
3. Update `overlays/uat/kustomization.yaml` ➔ ArgoCD Auto-Sync
       │
       ▼ (Mandatory Human Sign-off Gate)
4. Update `overlays/prod/kustomization.yaml` ➔ Argo Rollout Canary
```

## ArgoCD Application Definition
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: cloud-service-prod
  namespace: argocd
spec:
  project: default
  source:
    repoURL: 'https://github.com/org/gitops-infra.git'
    targetRevision: main
    path: overlays/prod
  destination:
    server: 'https://kubernetes.default.svc'
    namespace: prod-apps
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

## Guardrails
- **Production Gating:** Never configure automatic auto-sync with automated pruning directly on production without an active Canary analysis or manual approval step.
