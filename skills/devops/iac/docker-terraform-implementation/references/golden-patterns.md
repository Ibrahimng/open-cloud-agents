# Docker Terraform Golden Patterns & Secure Defaults

## 1. Provider Configuration (`versions.tf`)

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

---

## 2. Isolated Custom Bridge Network (`main.tf`)

```hcl
resource "docker_network" "internal_net" {
  name     = "${var.project_name}_${var.environment}_internal"
  driver   = "bridge"
  internal = true

  ipam_config {
    subnet  = "172.28.0.0/16"
    gateway = "172.28.0.1"
  }
}
```

---

## 3. Hardened Container Specification

```hcl
resource "docker_container" "hardened_service" {
  name  = "${var.project_name}-api"
  image = docker_image.service.image_id

  # Least privilege non-root UID
  user      = "10001:10001"
  read_only = true

  # Scratch writable directory
  tmpfs = {
    "/tmp" = "rw,noexec,nosuid,size=64m"
  }

  # Drop all capabilities
  capabilities {
    drop = ["ALL"]
  }

  # DoS Prevention: Resource Bounds
  memory     = 536870912 # 512 MB
  memory_swap = 536870912
  cpu_shares = 512

  networks_advanced {
    name = docker_network.internal_net.name
  }

  # Security options
  security_opts = [
    "no-new-privileges:true"
  ]

  restart = "on-failure"
}
```

---

## 4. Immutable Image Pinning with Digest

```hcl
resource "docker_image" "service" {
  name         = "ghcr.io/my-org/service:2.1.0@sha256:7b5f12a34b22c7104b20536be336f32e9be432e14a191f69fb4bbfaec9fa4c79"
  keep_locally = true
}
```

---

## 5. Secret Delivery via Environment File

```hcl
resource "docker_container" "app_with_secrets" {
  name  = "${var.project_name}-worker"
  image = docker_image.service.image_id

  user      = "10001:10001"
  read_only = true

  env_file = [
    "${path.module}/secrets/.env.vault.runtime"
  ]

  networks_advanced {
    name = docker_network.internal_net.name
  }
}
```

