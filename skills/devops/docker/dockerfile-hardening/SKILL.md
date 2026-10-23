---
name: dockerfile-hardening
description: Author multi-stage, rootless, distroless, and security-hardened Dockerfiles that produce minimal attack surfaces and pass Trivy/Grype vulnerability scans.
---

# Dockerfile Hardening & Multi-Stage Image Design

## Core Security Requirements
1. **Multi-Stage Builds**: Split build-time dependencies (compilers, SDKs, devDependencies) from the final runtime image.
2. **Never Run as Root**: Declare an explicit non-root user (`USER nonroot:nonroot` or `USER 10001:10001`).
3. **Use Minimal Base Images**: Prefer `gcr.io/distroless/*`, `scratch`, or Alpine over heavy Debian/Ubuntu base images.
4. **Deterministic Pinning**: Use explicit version tags and SHA-256 digest pinning for base images.
5. **No Embedded Secrets**: Never copy `.env`, credentials, private keys, or git tokens into the build layers.

## Reference Multi-Stage Dockerfile (Node.js / TypeScript Example)

```dockerfile
# ----------------------------------------------------
# Stage 1: Build & Compile
# ----------------------------------------------------
FROM node:22-alpine AS builder
WORKDIR /app

# Cache dependencies
COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install --frozen-lockfile

# Copy source and build
COPY tsconfig.json ./
COPY src/ ./src/
RUN pnpm build && pnpm prune --prod

# ----------------------------------------------------
# Stage 2: Minimal Distroless Runtime
# ----------------------------------------------------
FROM gcr.io/distroless/nodejs22-debian12:nonroot
WORKDIR /app

COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
COPY package.json ./

ENV NODE_ENV=production
USER nonroot

EXPOSE 8080
ENTRYPOINT ["node", "dist/index.js"]
```

## Image Vulnerability Audit Command
Before pushing any image to a container registry, scan for CVEs:
```bash
trivy image --severity HIGH,CRITICAL --exit-code 1 <image-name>:<tag>
```

