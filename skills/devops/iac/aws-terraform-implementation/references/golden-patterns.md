# AWS Terraform Golden Patterns & Secure Defaults

## 1. Provider & State Backend (`versions.tf` / `backend.tf`)

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
    bucket         = "tf-state-company-production-us-east-1"
    key            = "networking/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "tf-locks-company-production"
    encrypt        = true
  }
}
```

---

## 2. Global Tags & Locals (`locals.tf`)

```hcl
locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
    Owner       = var.owner
  }
}
```

---

## 3. Verified VPC Module (`main.tf`)

```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${var.project_name}-${var.environment}-vpc"
  cidr = var.vpc_cidr

  azs             = data.aws_availability_zones.available.names
  private_subnets = var.private_subnets
  public_subnets  = var.public_subnets

  enable_nat_gateway = true
  single_nat_gateway = var.environment != "production"

  tags = local.common_tags
}
```

---

## 4. S3 Bucket Secure Defaults

```hcl
resource "aws_s3_bucket" "secure_storage" {
  bucket = "${var.project_name}-${var.environment}-storage"

  lifecycle {
    prevent_destroy = true
  }

  tags = local.common_tags
}

resource "aws_s3_bucket_public_access_block" "secure_storage" {
  bucket                  = aws_s3_bucket.secure_storage.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "secure_storage" {
  bucket = aws_s3_bucket.secure_storage.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.main.arn
      sse_algorithm     = "aws:kms"
    }
  }
}
```

---

## 5. IAM Least-Privilege Role & Policy

```hcl
resource "aws_iam_role" "workload" {
  name = "${var.project_name}-${var.environment}-workload-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy" "workload_s3_access" {
  name = "s3-read-write"
  role = aws_iam_role.workload.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject", "s3:PutObject"]
      Resource = "${aws_s3_bucket.secure_storage.arn}/*"
    }]
  })
}
```
