# Enterprise HCL Style Guide & Naming Standards

## 1. Resource Naming Conventions
- Always use lowercase alphanumeric characters and underscores (`_`) in HCL identifiers:
  ```hcl
  # GOOD
  resource "aws_security_group" "alb_ingress" {}
  
  # FORBIDDEN
  resource "aws_security_group" "alb-ingress" {} # dashes forbidden in HCL identifiers
  resource "aws_security_group" "AlbIngress" {}
  ```
- **Singleton Resources:** If a module manages a single primary resource, name it `this`:
  ```hcl
  resource "aws_vpc" "this" {}
  resource "aws_route_table" "this" {}
  ```

## 2. Variable Validation Rules
Every input variable must have a description, an explicit type, and validation where applicable:
```hcl
variable "cidr_block" {
  type        = string
  description = "IPv4 CIDR block for the VPC (e.g. 10.0.0.0/16)."
  validation {
    condition     = can(cidrhost(var.cidr_block, 0))
    error_message = "The cidr_block value must be a valid IPv4 CIDR notation."
  }
}
```

## 3. Output Quality Standards
Always include a description and mark sensitive outputs:
```hcl
output "database_password" {
  value       = aws_db_instance.this.password
  description = "Root master database password."
  sensitive   = true
}
```

