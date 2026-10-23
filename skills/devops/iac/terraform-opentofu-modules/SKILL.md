---
name: terraform-opentofu-modules
description: Design, structure, and validate production-ready, reusable Terraform and OpenTofu modules following enterprise best practices and semantic versioning.
---

# Terraform & OpenTofu Reusable Module Architecture

## Purpose & Scope
This skill provides procedural standards and safety guardrails for authoring Terraform and OpenTofu infrastructure modules across AWS, Azure, and Google Cloud.

## Module Structure Standards
Every module must maintain a strict, minimal root layout:
```text
module-name/
├── main.tf          # Core resource declarations and local variables
├── variables.tf     # Explicitly typed input variables with descriptions & validation
├── outputs.tf       # Explicitly documented output values
├── versions.tf      # Required terraform version and provider constraints
└── README.md        # Generated via terraform-docs with inputs/outputs/examples
```

## Core Engineering Rules
1. **Explicit Types & Validations**:
   - Never declare a variable without a `type` constraint and `description`.
   - Use custom `validation` blocks for constrained parameters (e.g. environment names, IP CIDR ranges, naming patterns).
2. **Provider Pinning**:
   - Never hardcode provider configuration blocks (`provider "aws" {}`) inside a reusable module; providers must be passed from the root calling module.
   - Specify minimum and pessimistic provider versions in `versions.tf` using `~>`.
3. **No Hardcoded Secrets or Identifiers**:
   - Never embed AWS Account IDs, subscription IDs, VPC IDs, or passwords.
   - Use dynamic data sources or input variables.

## Step-by-Step Workflow
- [ ] 1. Define required providers and minimum terraform version in `versions.tf`.
- [ ] 2. Declare input variables in `variables.tf` with default values where sensible and custom validation blocks.
- [ ] 3. Implement target infrastructure in `main.tf` using consistent resource naming (`this` for singleton primary resources).
- [ ] 4. Expose critical attributes (IDs, ARNs, endpoints) in `outputs.tf` with clear descriptions.
- [ ] 5. Run static verification:
  ```bash
  tofu fmt -check -recursive
  tofu validate
  tflint --recursive
  ```
- [ ] 6. Generate module documentation via `terraform-docs markdown table . > README.md`.

## Example: Validated Input Variable
```hcl
variable "environment" {
  type        = string
  description = "Target deployment tier (dev, uat, prod)."
  validation {
    condition     = contains(["dev", "uat", "prod"], var.environment)
    error_message = "The environment variable must be one of: dev, uat, prod."
  }
}
```

