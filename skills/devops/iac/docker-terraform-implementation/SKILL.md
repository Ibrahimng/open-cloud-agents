---
name: docker-terraform-implementation
description: Implement, structure, and validate secure, production-grade container runtime configurations using the Docker Terraform provider, enforcing non-root execution, read-only root filesystems, dropped capabilities, resource limits, and network isolation.
---

# Docker Terraform Implementation & Quality Standard

## Purpose & Scope
This skill provides the operational standards, security baselines, and validation commands for orchestrating container workloads using the Docker Terraform provider (`kreuzwerker/docker`) based on machine-readable architecture plans from `.terraform-planning-files/`.

---

## Core Engineering Principles

1. **Least-Privilege Non-Root Execution**: Every container must run as an explicit non-root UID/GID (`user = "10001:10001"`). Forbid running as root (`UID 0`).
2. **Read-Only Root Filesystem**: Configure `read_only = true` to neutralize container file system tampering. Provide dedicated `tmpfs` mounts for temporary scratch space (`tmpfs = { "/tmp" = "rw,noexec,nosuid,size=64m" }`).
3. **Linux Capability Dropping**: Drop all Linux kernel capabilities (`capabilities { drop = ["ALL"] }`). Only re-add specific individual capabilities (e.g. `NET_BIND_SERVICE`) if strictly necessary and documented.
4. **Hard Resource Bounds (DoS Shield)**: Always enforce explicit resource bounds: `memory` (e.g., `536870912` for 512MB), `memory_swap`, and `cpu_shares`. Never allow unconstrained container memory consumption.
5. **Custom Network Isolation**: Place containers on user-defined bridge networks (`docker_network` with `internal = true` for backend tiers). Never attach containers to the default bridge network or host network.
6. **Immutable Image Pinning**: Always reference container images by immutable cryptographic SHA256 digests (`name = "registry/app:1.0.0@sha256:..."`) rather than mutable tags (`:latest`).
7. **Zero Plaintext Secrets**: Supply credentials via environment files, external secret mounts, or Docker secrets. Never embed sensitive passwords in plain HCL `env` blocks.

---

## Step-by-Step Implementation Workflow

### Step 1: Read the Plan
- Check `.terraform-planning-files/` for an existing plan (`INFRA.docker.{goal}.md` or `INFRA.{goal}.md`).
- If found, implement exactly what the plan specifies without unauthorized deviation.
- If not found, request that the planning agent produce the plan or confirm minimal scope.

### Step 2: Implement Resources
- **Isolated Custom Bridge Network**:
  ```hcl
  resource "docker_network" "app_net" {
    name     = "${var.project_name}_${var.environment}_net"
    driver   = "bridge"
    internal = true
  }
  ```
- **Hardened Container Configuration**:
  ```hcl
  resource "docker_container" "hardened_service" {
    name  = "${var.project_name}-service"
    image = docker_image.app.image_id

    user      = "10001:10001"
    read_only = true

    tmpfs = {
      "/tmp" = "rw,noexec,nosuid,size=64m"
    }

    capabilities {
      drop = ["ALL"]
    }

    memory     = 536870912 # 512 MB
    cpu_shares = 512

    networks_advanced {
      name = docker_network.app_net.name
    }

    restart = "on-failure"
  }
  ```
- **Digest-Pinned Image**:
  ```hcl
  resource "docker_image" "app" {
    name         = "myregistry.azurecr.io/my-service:1.2.0@sha256:45b23dee08af5e43a7fa6c4e1aa9f80fde3299b4c044237742c0d46ba9f67ef0"
    keep_locally = true
  }
  ```

### Step 3: Code Review Checklist
Before submitting code for review, verify:
- [ ] Container runs as an explicit non-root user (`user = "10001:10001"`)
- [ ] Read-only root filesystem enforced (`read_only = true`) with dedicated `tmpfs` mounts
- [ ] All Linux capabilities dropped (`capabilities { drop = ["ALL"] }`)
- [ ] Memory limit specified (`memory`) and CPU shares allocated (`cpu_shares`)
- [ ] Workloads attached to custom user-defined bridge network (no default bridge or host network)
- [ ] Images pinned to immutable SHA256 digests
- [ ] Zero plaintext secrets in `env = [...]` configuration blocks
- [ ] Outputs cleanly defined and variables have descriptions and validations

### Step 4: Validation
Execute and fix any findings:
```bash
terraform fmt -recursive
terraform validate
terraform plan -out=tfplan
```

---

## File Structure Standards

Standard directory layout for Docker Terraform projects:
```text
infrastructure/docker/
├── main.tf       # Container and network definitions
├── variables.tf  # Image tags, memory limits, port bindings
├── outputs.tf    # Container IDs, network names
├── locals.tf     # Common labels and configuration maps
├── versions.tf   # kreuzwerker/docker provider requirements
└── modules/
    └── <module>/
        ├── main.tf
        ├── variables.tf
        └── outputs.tf
```

Standard provider configuration:
```hcl
terraform {
  required_version = ">= 1.5"
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {
  host = "unix:///var/run/docker.sock"
}
```
