---
name: aws-terraform-implementation
description: Implement, structure, and validate secure, production-grade AWS Terraform infrastructure based on machine-readable plans in .terraform-planning-files/, enforcing module-first registry patterns, IAM least-privilege, and S3 secure defaults.
---

# AWS Terraform Implementation & Quality Standard

## Purpose & Scope
This skill provides the operational standards, code patterns, and validation commands for implementing AWS infrastructure in `infrastructure/` based on machine-readable architecture plans from `.terraform-planning-files/`.

---

## Core Engineering Principles

1. **Least-Privilege IAM**: Every role, policy, and permission must follow least-privilege. Never use wildcard `*` actions unless strictly required and documented.
2. **Encryption Everywhere**: Enable encryption at rest and in transit for all supported resources using AWS KMS Customer Managed Keys (CMKs).
3. **VPC Isolation**: Place workloads in private subnets by default, exposing public subnets only for load balancers. Security groups must have minimal ingress with zero `0.0.0.0/0` exposure on sensitive ports.
4. **Tagging Strategy**: Apply consistent resource tags via root `local.common_tags`.
5. **State Management**: Use remote S3 state storage with DynamoDB state locking. Never commit or use local state for shared infrastructure.
6. **Module-First**: Standardize on verified `terraform-aws-modules` from the Terraform Registry. Always verify and fetch the latest semantic version.

---

## Step-by-Step Implementation Workflow

### Step 1: Read the Plan
- Check `.terraform-planning-files/` for an existing plan (`INFRA.{goal}.md`).
- If found, implement exactly what the plan specifies without unauthorized deviation.
- If not found, request that the planning agent produce the plan, or proceed with minimal scope.

### Step 2: Implement Resources
- **VPC Module**:
  ```hcl
  module "vpc" {
    source  = "terraform-aws-modules/vpc/aws"
    version = "~> 5.0"

    name            = var.vpc_name
    cidr            = var.vpc_cidr
    azs             = data.aws_availability_zones.available.names
    private_subnets = var.private_subnets
    public_subnets  = var.public_subnets

    enable_nat_gateway = true
    single_nat_gateway = var.environment != "production"

    tags = local.common_tags
  }
  ```
- **IAM Policy Least-Privilege**:
  ```hcl
  resource "aws_iam_role_policy" "example" {
    role = aws_iam_role.example.id
    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [{
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject"]
        Resource = "${aws_s3_bucket.example.arn}/*"
      }]
    })
  }
  ```
- **S3 Secure Defaults**:
  ```hcl
  resource "aws_s3_bucket_public_access_block" "example" {
    bucket                  = aws_s3_bucket.example.id
    block_public_acls       = true
    block_public_policy     = true
    ignore_public_acls      = true
    restrict_public_buckets = true
  }
  ```

### Step 3: Code Review Checklist
Before submitting changes for review, verify:
- [ ] IAM policies use least-privilege (no `*` actions without justification)
- [ ] All secrets use Secrets Manager or SSM Parameter Store (not hardcoded)
- [ ] S3 buckets have public access blocked (`aws_s3_bucket_public_access_block`)
- [ ] Encryption enabled (KMS CMK, SSL/TLS)
- [ ] Resources placed in private subnets unless explicitly public-facing
- [ ] Security groups have minimal ingress, no `0.0.0.0/0` on sensitive ports
- [ ] Tagging applied consistently (`local.common_tags`)
- [ ] `lifecycle` blocks used where appropriate (`prevent_destroy` for stateful resources)
- [ ] Outputs exported for cross-module consumption
- [ ] Variables have descriptions and validation blocks

### Step 4: Validation
Execute and fix any findings:
```bash
terraform fmt -recursive
terraform validate
terraform plan -out=tfplan
```

---

## File Structure Standards

Standard directory layout for `infrastructure/`:
```text
infrastructure/
├── main.tf       # Root module, primary resource wiring
├── variables.tf  # Input variables with descriptions and validation
├── outputs.tf    # Root outputs
├── locals.tf     # Local values and common tags
├── versions.tf   # Required providers and versions
├── backend.tf    # S3/DynamoDB state backend
└── modules/
    └── <module>/
        ├── main.tf
        ├── variables.tf
        └── outputs.tf
```

Standard provider and backend configuration:
```hcl
terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket         = "<state-bucket>"
    key            = "<path>/terraform.tfstate"
    region         = "<region>"
    dynamodb_table = "<lock-table>"
    encrypt        = true
  }
}
```
