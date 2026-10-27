# Container Hardening & Distroless Cheat Sheet

## Distroless vs Alpine vs Debian

| Aspect | Distroless (`gcr.io/distroless/*`) | Alpine (`alpine:3.20`) | Debian / Ubuntu (`debian:bookworm`) |
|---|---|---|---|
| **Image Size** | Minimal (~20-60MB) | Very small (~5-15MB) | Heavy (~120-250MB) |
| **Shell Included?** | **NO** (`/bin/sh` absent) | Yes (`/bin/sh` via busybox) | Yes (`/bin/bash`, `/bin/sh`) |
| **Package Manager?** | **NO** (no `apt`, `apk`) | Yes (`apk`) | Yes (`apt`) |
| **CVE Attack Surface** | Near Zero | Very low | Moderate to High |
| **Best Used For** | Production runtime stages | Multi-stage build stages | Local debugging / build tools |

## Essential Dockerfile Rules
1. Never execute `USER root` in the final stage.
2. Never store API keys in `ENV` instructions (they remain in image layer history).
3. Always add a `.dockerignore` excluding `.git`, `node_modules`, `.env*`, and build caches.

